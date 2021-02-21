from PIL import Image
from scipy.misc import imresize
import numpy as np
from keras.models import load_model
import tensorflow as tf


DEFAULT_INPUT_SIZE = (224, 224)
THRESHOLD = 255 / 2

# Global variables for the model and graph
model = None
graph = None


def model_prediction(image):
    with graph.as_default():
        prediction = model.predict(image[None, :, :, :])
    prediction = prediction.reshape((DEFAULT_INPUT_SIZE[0], DEFAULT_INPUT_SIZE[1], -1))
    return prediction


def prepare():
    global model, graph

    if model is None:
        print("Loading tensorflow model...")
        model = load_model("./tfmodel/main_model.hdf5", compile=False)
        print("Tensorflow model loaded!")

    if graph is None:
        graph = tf.get_default_graph()


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
