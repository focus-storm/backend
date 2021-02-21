import model_processor
from PIL import Image
from flask import request


class Driver:

    model_processor.prepare()

    def handle_file(self):
        img = Image.open("test/corgi.jpg")
        processed_img = model_processor.process_image(img)
        print("File processed")
        return processed_img


def main():
    driver = Driver()
    res = driver.handle_file()
    res.save('test/test.png')  # Rename
    res.show()  # Remove this if image won't be displayed in IDE


if __name__ == '__main__':
    main()
