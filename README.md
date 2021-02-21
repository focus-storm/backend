# Focus

**Focus** is a Google Chrome Extension, that utilizes machine learning to
 remove the background of an image. Although Focus can remove background
  on all images, it works best with images that contain people.


### How Focus Works :computer: 
Focus is dependent on a pre-trained Tensorflow model explained 
[here](https://towardsdatascience.com/background-removal-with-deep-learning-c4f2104b3157).
Through semantic segmentation, Focus will classify the object as either a
the background, or an object. 
   
#### Running with Flask
To run Flask:
```
cd src
export FLASK_APP=app.py
flask run
```

#### Running from Source
```
pyenv shell 3.7x
python app.js
```
