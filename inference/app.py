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


app = Flask(__name__)
# app.run(port=5000, debug=True)
config = {
    'output_nc': 3,
    'input_nc': 3,
    'size': (256, 256),
    'model_path': '/home/freefridays/github/espresso-cyclegan/snapshots/2020-10-29_09_23_35/51_9000.pt'
}
model = Model(config)


def pad_factor(img, factor=16):
    W, H = img.size
    pad_W = (factor - (W % factor)) % factor
    pad_H = (factor - (H % factor)) % factor
    padding = (pad_W // 2, pad_H // 2, pad_W - (pad_W // 2), pad_H - (pad_H // 2))
    img_pad = ImageOps.expand(img, padding)
    return img_pad, pad_W, pad_H


def original_region(img, pad_H, pad_W):
    return img[pad_H // 2:-max((pad_H - (pad_H // 2)), 1), pad_W // 2:-max((pad_W - (pad_W // 2)), 1), :]


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

        # resize
        img = Image.open(io.BytesIO(img_bytes)).convert('RGBA')
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
                                    alpha_matting=opt.get('am')=='True',
                                    alpha_matting_foreground_threshold=eval(opt.get('amft')),
                                    alpha_matting_background_threshold=eval(opt.get('ambt')),
                                    alpha_matting_erode_structure_size=eval(opt.get('amess')))
            # get alpha channel
            img_nobg = np.array(Image.open(io.BytesIO(img_bytes_nobg)).convert('RGBA'))
            Image.fromarray(img_nobg).save('tmp.png')
            assert img_nobg.shape[-1] == 4  # must have alpha channel
            alpha = np.expand_dims(img_nobg[:, :, -1], axis=-1)
            # alpha[alpha < 20] = 0
            # alpha[alpha >= 20] = 255

            output_img = model.inference(img_bytes)
            output_img = np.array(output_img)
            output_img = np.concatenate([output_img, alpha], axis=-1)
            output_img = original_region(output_img, pad_H, pad_W)
            output_img = Image.fromarray(output_img)
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
