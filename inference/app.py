# https://tutorials.pytorch.kr/intermediate/flask_rest_api_tutorial.html
import io
import base64
from transfer import Model
from flask import Flask, jsonify, request
from time import time
import magic

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
    if request.method == 'POST' and request.files.get('img'):
        t0 = time()

        img_bytes = request.files['img'].read()
        extention = magic.from_buffer(img_bytes).split()[0].upper()

        if extention not in ['JPEG', 'PNG', 'JPG']:
            res = {
                'status': True,
                'message': 'please request with valid image (only supports JPEG or PNG)'
            }
            return jsonify(res)

        output_img = model.inference(img_bytes)
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
