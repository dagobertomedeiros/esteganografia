from flask import Flask, jsonify, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_cors import CORS
from PIL import Image
import os.path
import numpy as np

IMAGES = [{'id': '0',
           'path': os.path.abspath(f'images\\big_brother_is_watching_u_original.bmp')}
          ]
UPLOADER_FOLDER = os.path.abspath(f'images')
EXTENSIONS = {'.bmp'}
NUM = 0

DEBUG = True

app = Flask(__name__)
app.config['UPLOADER_FOLDER'] = UPLOADER_FOLDER
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})


@app.route('/')
def home():
    return 'API online!'


@app.route('/image', methods=['POST', 'GET'])
def image():
    if request.method == 'POST':
        # if 'file' not in request.files:
        #    print('passou aqui 1')
        #    flash('No file')
        #    return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('passou aqui 2')
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print('passou aqui 3')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOADER_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    elif request.method == 'GET':
        return jsonify('ID image -> ' + str(len(IMAGES)))


@app.route('/encode', methods=['POST'])
def encode_image(id, message):
    img = IMAGES[id]['path']
    img = Image.open(img, 'r')
    pixel_num = 0
    if img.mode == 'RGB':
        pixel_num = 3
    elif img.mode == 'RGBA':
        pixel_num = 4
    array_pixels = np.array(list(img.getdata()))
    total_pixels = int(array_pixels.size / pixel_num)
    width, height = img.size
    message += '.'
    binary_message = ''.join([format(ord(i), '08b') for i in message])
    necessary_pixels = len(binary_message)
    if necessary_pixels < total_pixels:
        i = 0
        for p in range(total_pixels):
            for q in range(0, 3):
                if i < necessary_pixels:
                    array_pixels[p][q] = int(bin(array_pixels[p][q])[2:9] + binary_message[i], 2)
                    i += 1
        array_pixels = array_pixels.reshape(height, width, pixel_num)
        enc_img = Image.fromarray(array_pixels.astype('uint8'), img.mode)
        enc_img.save('path')
        return jsonify(enc_img)
    else:
        return jsonify('Não foi possível codificar a imagem')


@app.route('/decode', methods=['GET'])
def decode_image(id):
    data = data_image(IMAGES[id]['path'])
    array_pixels = data['array_pixels']
    total_pixels = data['total_pixels']
    hid_bin_message = ''
    for p in range(total_pixels):
        for q in range(0, 3):
            hid_bin_message += (bin(array_pixels[p][q])[2:][-1])
    hid_bin_message = [hid_bin_message[i:i + 8] for i in range(0, len(hid_bin_message), 8)]
    hid_message = ''
    for i in range(len(hid_bin_message)):
        hid_message += chr(int(hid_bin_message[i], 2))
        hid_message = f'{hid_message}'
    return jsonify(hid_message)


def data_image(path: str):
    img = IMAGES[id]['path']
    img = Image.open(img, 'r')
    pixel_num = 0
    if img.mode == 'RGB':
        pixel_num = 3
    elif img.mode == 'RGBA':
        pixel_num = 4
    array_pixels = np.array(list(img.getdata()))
    total_pixels = int(array_pixels.size / pixel_num)
    width, height = img.size
    return {'array': array_pixels,
            'total_pixels': total_pixels,
            'wid': width,
            'hei': height}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSIONS


if __name__ == '__main__':
    app.run()
