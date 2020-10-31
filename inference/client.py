import requests
import io
from PIL import Image
import base64


res = requests.post('http://127.0.0.1:5000/inference',
                    files={'img': open('/home/freefridays/github/espresso-cyclegan/examples/cup.png', 'rb')})

res = res.json()

print(res['status'], res['elapsed_time'])
img = base64.b64decode(res['img'])
Image.open(io.BytesIO(img)).save('./result.png')
