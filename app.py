import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import urllib.request
import threading
import time
from PIL import Image
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
import tensorflow as tf
from os import listdir
from os.path import getctime, join

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
CORS(app)

DEFAULT_INPUT_SIZE = (224, 224)
THRESHOLD = 255 / 2

# Global variables for the model and graph
model = load_model("tfmodel/main_model.hdf5", compile=False)
graph = tf.get_default_graph()


def model_prediction(image):
    with graph.as_default():
        prediction = model.predict(image[None, :, :, :])
    prediction = prediction.reshape((DEFAULT_INPUT_SIZE[0], DEFAULT_INPUT_SIZE[1], -1))
    return prediction


# def prepare():
#     global model, graph

#     if model is None:
#         print("Loading tensorflow model...")
#         model = load_model("tfmodel/main_model.hdf5", compile=False)
#         print("Tensorflow model loaded!")

#     if graph is None:
#         graph = tf.get_default_graph()


def convert_input(image):
    """
    Convert image to values that can be used with trained model.
    :param image: an Image
    :return: Matrix of values between 0 - 1
    """
    image = image.resize(DEFAULT_INPUT_SIZE)
    return np.array(image) / 255.0


def process_image(image):

    normalized = convert_input(image)

    # Remove alpha channels
    rgbs = normalized[:, :, 0:3]

    # Index 0 is background, index 1 is person
    classification = model_prediction(rgbs)

    person = classification[:, :, 1]
    classification = imresize(person, (image.height, image.width))

    classification[classification > THRESHOLD] = 255
    classification[classification < THRESHOLD] = 0

    # Re-add alpha matrix
    output = np.array(image)[:, :, 0:3]
    output = np.append(output, classification[:, :, None], axis=-1)
    return Image.fromarray(output)

def handle_file():
    path = "./uploads/"
    files = [join(path, file) for file in listdir(path)]
    newest = max(files, key=getctime)

    img = Image.open(newest)
    processed_img = process_image(img)
    print("File processed")
    return processed_img, newest.rsplit('/', -1)[2]



# def validate_image(stream):
#     header = stream.read(512)  # 512 bytes should be enough for a header check
#     stream.seek(0)  # reset stream pointer
#     format = imghdr.what(None, header)
#     if not format:
#         return None
#     return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return '''
<!doctype html>
<html>
  <head>
    <title>File Upload</title>
  </head>
  <body>
    <h1>File Upload</h1>
    <form method="POST" action="" enctype="multipart/form-data">
      <p><input type="text" name="url"></p>
      <p><input type="submit" value="Submit"></p>
    </form>
  </body>
</html>'''


@app.route('/', methods=['POST'])
def upload_files():
    image_url = request.form["url"]
    urllib.request.urlretrieve(image_url, "uploads/local-filename.jpg")
    res, filename = handle_file()
    res.save("./output/processed.png")
    # uploaded_file = request.files['file']
    # filename = secure_filename(uploaded_file.filename)
    # if filename != '':
    #     file_ext = os.path.splitext(filename)[1]
    #     if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
    #             file_ext != validate_image(uploaded_file.stream):
    #         abort(400)
    #     uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


def main():
    model_processor.prepare()
    x = threading.Thread(target=model_processor.prepare)
    x.start()
    time.sleep(15)
    res, filename = driver.handle_file()
    x.join()
    res.save("/output/processed.png")


if __name__ == '__main__':
    app.run(host='0.0.0.0')

