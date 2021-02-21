from src import model_processor
from PIL import Image
from os import listdir
from os.path import getctime, join


def handle_file():
    path = "src/uploads/"
    files = [join(path, file) for file in listdir(path)]
    newest = max(files, key=getctime)

    img = Image.open(newest)
    processed_img = model_processor.process_image(img)
    print("File processed")
    return processed_img, newest.rsplit('/', -1)[2]
