import os
from flask import Flask, request, redirect, url_for, send_from_directory, send_file, render_template
from flask_cors import CORS
import urllib.request
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


def convert_input(image):
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
    return send_file("./output/processed.png", mimetype='image/png')

@app.route('/output/')
def ouput():
    return render_template("image.html")

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0')

