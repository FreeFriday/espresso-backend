# https://tutorials.pytorch.kr/intermediate/flask_rest_api_tutorial.html
import io
from base64 import encodebytes
from transfer import Model
from flask import Flask, jsonify, request
from time import time

app = Flask(__name__)
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
    if request.method == 'POST':
        t0 = time()

        img_bytes = request.files['img'].read()
        output_img = model.inference(img_bytes)
        byte_arr = io.BytesIO()
        output_img.save(byte_arr, 'PNG')
        encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')  # encode as base64

        t1 = time()
        res = {
            'status': True,
            'elapsed_time': t1 - t0,
            'img': encoded_img
        }
    else:
        res = {
            'status': False,
            'message': 'please request using POST method'
        }

    return jsonify(res)
