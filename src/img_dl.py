import requests  # to get image from the web
import shutil  # to save it locally
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import os
import platform
import sys
import getopt


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)


# This code downloads the image.
def download_image(image_url: str):
    filename = image_url.split("/")[-1]

    r = requests.get(image_url, stream=True)
    fpath = os.path.join(os.getcwd(), "imgs")
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(os.path.join(os.getcwd(), "imgs", filename), 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print('Image successfully Downloaded: ', filename)
    else:
        print('Image couldn\'t be retrieved')


def main():
    URL = str(input("Enter URL of page with images: "))
    sys_type = platform.system()
    if sys_type == "Darwin":
        driver_path = "/usr/local/bin/chromedriver"
    elif sys_type == "Windows":
        driver_path = os.path.join(os.getcwd(),
                                   "utilities",
                                   "chromedriver_win32",
                                   "chromedriver.exe")

    browser = webdriver.Chrome(driver_path)
    browser.get(URL)

    # Give the browser time to load all content.
    time.sleep(3)
    content = browser.find_elements_by_css_selector("img")
    for e in content:
        start = e.get_attribute('src')
        soup = BeautifulSoup(start, features="html.parser")
        content = soup.get_text()
        if "blank.gif" not in content:
            download_image(content)
            print("***")


if __name__ == "__main__":
    main()
