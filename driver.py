import model_processor
from PIL import Image
from io import BytesIO
from flask import request


class Driver:

    def __init__(self):
        model_processor.prepare()

    def handle_file(self):

        img = Image.open("test/corgi.jpg")
        processed = model_processor.convert_input(img)
        x = model_processor.process_image(processed)
        print("File processed, uploading to Slack")
        return x


def main():
    driver = Driver()
    res = driver.handle_file()
    print(res)


if __name__ == '__main__':
    main()
