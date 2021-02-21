import imghdr
import os
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import urllib.request
from src import driver, model_processor
import threading
import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
CORS(app)


def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html', files=files)


@app.route('/', methods=['POST'])
def upload_files():
    image_url = request.form["url"]
    urllib.request.urlretrieve(image_url, "uploads/local-filename.jpg")

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
    res.save("src/output/processed.png")


if __name__ == '__main__':
    main()

