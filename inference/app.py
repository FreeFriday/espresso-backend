# https://tutorials.pytorch.kr/intermediate/flask_rest_api_tutorial.html
import io
import base64
from transfer import Model
from flask import Flask, jsonify, request
from time import time
import magic
from rembg.bg import remove
from PIL import Image, ImageOps
import numpy as np
from glob import glob
from random import randint
from postprocessor import erosion


app = Flask(__name__)
# app.run(port=5000, debug=True)
config = {
    'output_nc': 3,
    'input_nc': 3,
    'size': (256, 256),
    'model_path': '/home/freefridays/github/espresso-cyclegan/68_10405.pt'
        # '/home/freefridays/github/espresso-cyclegan/64_10405.pt' # openimage + no_resize_som
        # '/home/freefridays/github/espresso-cyclegan/59_10405.pt' # openimage + no_resize_som
        #'/home/freefridays/github/espresso-cyclegan/55_10405.pt' # openimage
        #'/home/freefridays/github/espresso-cyclegan/snapshots/2020-10-29_09_23_35/51_9000.pt',
}
model = Model(config)
data_paths = glob('/home/freefridays/datasets/photo2som/trainA/*')
ALPHA_THRESHOLD = 5
SIZE_THRESHOLD = 1200


def pad_factor(img, factor=16):
    W, H = img.size
    pad_W = (factor - (W % factor)) % factor
    pad_H = (factor - (H % factor)) % factor
    # padding = (pad_W // 2, pad_H // 2, pad_W - (pad_W // 2), pad_H - (pad_H // 2))
    padding = ((pad_H // 2, pad_H - (pad_H // 2)), (pad_W // 2, pad_W - (pad_W // 2)), (0, 0))
    # img_pad = ImageOps.expand(img, padding)

    img_np = np.array(img)
    img_pad = np.pad(img_np, padding, 'reflect')
    img_pad = Image.fromarray(img_pad)

    return img_pad, pad_W, pad_H


def original_region(img, pad_H, pad_W):
    h0 = pad_H // 2
    h1 = -(pad_H - (pad_H // 2)) if pad_H != 0 else None
    w0 = pad_W // 2
    w1 = -(pad_W - (pad_W // 2)) if pad_W != 0 else None
    return img[h0:h1, w0:w1, :]


@app.route('/hi', methods=['GET'])
def hi():
    return 'Hi there!\n'


@app.route('/inference', methods=['POST'])
def inference():
    """
    - img: base64-encoded file
    """

    print(request)
    print(request.files)
    print(request.args)
    if request.method == 'POST' and request.files.get('img'):
        t0 = time()
        opt = request.args
        img_bytes = request.files['img'].read()
        extention = magic.from_buffer(img_bytes).split()[0].upper()

        if extention not in ['JPEG', 'PNG', 'JPG']:
            res = {
                'status': True,
                'message': 'please request with valid image (only supports JPEG or PNG)'
            }
            return jsonify(res)

        # resize and padding
        img = Image.open(io.BytesIO(img_bytes)).convert('RGBA')
        W, H = img.size
        if W >= SIZE_THRESHOLD or H >= SIZE_THRESHOLD:
            if W > H:
                img = img.resize((SIZE_THRESHOLD, int(H * SIZE_THRESHOLD/W)), Image.ANTIALIAS)
            else:
                img = img.resize((int(W * SIZE_THRESHOLD / H), SIZE_THRESHOLD), Image.ANTIALIAS)
        img_pad, pad_W, pad_H = pad_factor(img, factor=16)
        img_bytes = io.BytesIO()
        img_pad.save(img_bytes, 'PNG')
        img_bytes = img_bytes.getvalue()

        if opt.get('bgrmv') == 'false':
            output_img = model.inference(img_bytes)
            output_img = np.array(output_img)
            output_img = original_region(output_img, pad_H, pad_W)
            output_img = Image.fromarray(output_img)
            byte_arr = io.BytesIO()
            output_img.save(byte_arr, 'PNG')
        else:
            # remove background
            img_bytes_nobg = remove(img_bytes,
                                    alpha_matting=opt.get('am').lower()=='true',
                                    alpha_matting_foreground_threshold=int(opt.get('amft')),
                                    alpha_matting_background_threshold=int(opt.get('ambt')),
                                    alpha_matting_erode_structure_size=int(opt.get('amess')))
            # get alpha channel
            img_nobg = np.array(Image.open(io.BytesIO(img_bytes_nobg)).convert('RGBA'))
            Image.fromarray(img_nobg).save('tmp.png')
            assert img_nobg.shape[-1] == 4  # must have alpha channel
            alpha = np.expand_dims(img_nobg[:, :, -1], axis=-1)
            alpha[alpha < ALPHA_THRESHOLD] = 0

            output_img = model.inference(img_bytes)
            output_img = np.array(output_img)
            output_img = np.concatenate([output_img, alpha], axis=-1)
            output_img = original_region(output_img, pad_H, pad_W)
            output_img = Image.fromarray(output_img)
            output_img = output_img.crop(output_img.getbbox())  # crop bounding box
            byte_arr = io.BytesIO()
            output_img.save(byte_arr, 'PNG')

        encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64

        t1 = time()
        res = {
            'status': True,
            'elapsed_time': t1 - t0,
            'img': encoded_img
        }
    else:
        res = {
            'status': False,
            'message': 'please request with image using POST method'
        }

    return jsonify(res)


@app.route('/random', methods=['GET'])
def random():
    """
    - img: base64-encoded file
    """

    print(request)
    print(request.files)
    print(request.args)
    if request.method == 'GET':
        t0 = time()
        opt = request.args
        img_path = data_paths[randint(0, len(data_paths)-1)]
        img_ori = Image.open(img_path).convert('RGBA')
        img_pad, pad_W, pad_H = pad_factor(img_ori, factor=16)
        img_bytes = io.BytesIO()
        img_pad.save(img_bytes, 'PNG')
        img_bytes = img_bytes.getvalue()
        encoded_in = base64.encodebytes(img_bytes).decode('ascii')  # encode as base64

        if opt.get('bgrmv') == 'false':
            output_img = model.inference(img_bytes)
            output_img = np.array(output_img)
            output_img = original_region(output_img, pad_H, pad_W)
            output_img = Image.fromarray(output_img)
            byte_arr = io.BytesIO()
            output_img.save(byte_arr, 'PNG')
        else:
            # remove background
            img_bytes_nobg = remove(img_bytes,
                                    alpha_matting=opt.get('am').lower()=='true',
                                    alpha_matting_foreground_threshold=int(opt.get('amft')),
                                    alpha_matting_background_threshold=int(opt.get('ambt')),
                                    alpha_matting_erode_structure_size=int(opt.get('amess')))
            # get alpha channel
            img_nobg = np.array(Image.open(io.BytesIO(img_bytes_nobg)).convert('RGBA'))
            Image.fromarray(img_nobg).save('tmp.png')
            assert img_nobg.shape[-1] == 4  # must have alpha channel
            alpha = np.expand_dims(img_nobg[:, :, -1], axis=-1)

            # inference
            output_img = model.inference(img_bytes)
            output_img = np.array(output_img)
            output_img = np.concatenate([output_img, alpha], axis=-1)
            output_img = original_region(output_img, pad_H, pad_W)
            output_img = Image.fromarray(output_img)
            byte_arr = io.BytesIO()
            output_img.save(byte_arr, 'PNG')

        encoded_out = base64.encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64

        t1 = time()
        res = {
            'status': True,
            'elapsed_time': t1 - t0,
            'img_in': encoded_in,
            'img_out': encoded_out,
        }
    else:
        res = {
            'status': False,
            'message': 'please request with image using GET method'
        }

    return jsonify(res)


@app.route('/postprocess', methods=['POST'])
def postprocess():
    """
    - img: base64-encoded file
    """

    print(request)
    print(request.files)
    print(request.args)
    if request.method == 'POST' and request.files.get('img'):
        t0 = time()
        opt = request.args
        img_bytes = request.files['img'].read()
        extention = magic.from_buffer(img_bytes).split()[0].upper()

        if extention not in ['JPEG', 'PNG', 'JPG']:
            res = {
                'status': True,
                'message': 'please request with valid image (only supports JPEG or PNG)'
            }
            return jsonify(res)

        # resize
        img = Image.open(io.BytesIO(img_bytes)).convert('RGBA')
        W, H = int(opt.get('w')), int(opt.get('h'))
        itr = int(opt.get('level'))
        use_bi = opt.get('bi') == '1'
        img = img.resize((W, H), Image.ANTIALIAS)
        img = np.array(img)

        # erode and apply bilateral filter
        if itr >= 1:
            img = erosion(img, itr=itr, bilateral_filter=use_bi)

        output_img = Image.fromarray(img)
        byte_arr = io.BytesIO()
        output_img.save(byte_arr, 'PNG')
        encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64

        t1 = time()
        res = {
            'status': True,
            'elapsed_time': t1 - t0,
            'img': encoded_img
        }
    else:
        res = {
            'status': False,
            'message': 'please request with image using POST method'
        }

    return jsonify(res)

