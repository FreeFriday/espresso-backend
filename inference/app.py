# https://tutorials.pytorch.kr/intermediate/flask_rest_api_tutorial.html
import io
import base64
from transfer import Model
from flask import Flask, jsonify, request
from time import time
import magic
from rembg.bg import remove
from PIL import Image
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

        if opt.get('bgrmv') == 'false':
            output_img = model.inference(img_bytes)
            byte_arr = io.BytesIO()
            output_img.save(byte_arr, 'PNG')
        else:
            # resize
            img_resize = Image.open(io.BytesIO(img_bytes)).convert('RGBA').resize((256, 256), Image.LANCZOS)
            img_bytes = io.BytesIO()
            img_resize.save(img_bytes, 'PNG')
            img_bytes = img_bytes.getvalue()

            # remove background
            # img_bytes_nobg = remove(img_bytes,
            #                         alpha_matting=opt.get('am'),
            #                         alpha_matting_foreground_threshold=opt.get('amft'),
            #                         alpha_matting_background_threshold=opt.get('ambt'),
            #                         alpha_matting_erode_structure_size=opt.get('amess'))
            img_bytes_nobg = remove(img_bytes, alpha_matting=True)

            # get alpha channel
            img_nobg = np.array(Image.open(io.BytesIO(img_bytes_nobg)).convert('RGBA'))
            Image.fromarray(img_nobg).save('tmp.png')
            assert img_nobg.shape[-1] == 4  # must have alpha channel
            alpha = np.expand_dims(img_nobg[:, :, -1], axis=-1)
            alpha[alpha < 20] = 0
            alpha[alpha >= 20] = 255

            output_img = model.inference(img_bytes)
            output_img = np.array(output_img)
            output_img = Image.fromarray(np.concatenate([output_img, alpha], axis=-1))
            byte_arr = io.BytesIO()
            output_img.save(byte_arr, 'PNG')

        encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64

        # encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64

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
