# faceorienter

A small proof of concept which fixes the orientation of images containing (frontal) faces. Comes with a RESTful API.

(Requires Python3.3+)

### Problem

It's not always possible to extract information on a portrait image's orientation from its EXIF data. This 
application should correctly predict the orientation of an image containing a face, and fix it accordingly:

![](https://i.imgur.com/YEeoQpW.png)


### Solution

This solution uses two pre-trained dlib models: dlib's default face detector, 
and a 5 point facial landmarking model, which identifies the corners of the eyes and the bottom of the nose
(from [github.com/davisking/dlib-models](https://github.com/davisking/dlib-models))

The following steps are taken to predict an image's orientation:

1. Convert the image to grayscale
2. Try to detect a face in the image and "draw" a rectangle around it
    - If no face can be detected, keep rotating the image by 90 degrees and try again
3. Keep the image in the orientation in which a face was detected, and find the facial landmarks in the rectangle
4. We can now use the landmarks (i.e. the eye and nose coordinates) to predict the image's orientation. We can assume that:
    - If nose is between eyes on x-axis and below eyes on y-axis: *DOWN* (correctly oriented)
    - If nose is between eyes on x-axis and above eyes on y-axis: *UP*
    - If nose is left of eyes on x-axis and inbetween eyes on y-axis: *LEFT*
    - If nose is right of eyes on x-axis and inbetween eyes on y-axis: *RIGHT*
5. If any rotations were applied to the image during face detection, substract them


### How to use

#### Installation

Make sure `opencv` and its dependencies are installed. Then run `pip install .` from the project root to install the package.

#### Python API

```python
from faceorienter import FaceOrienter

fo = FaceOrienter('path/to/image.jpg')
fo.predict_orientation()  # Detect the image's orientation (returns either `down`, `up`, `left`, or `right`)
fo.fix_orientation('path/to/new/image.jpg')  # Corrects the orientation and writes the new image to the specified path
```

#### RESTful API
Run the server using `python -m faceorienter.server --port <PORT>` (default port `5000`).

You can now fix image orientations by sending a `POST` request to `http://<SERVER_ADDRESS>:<PORT>/orient` (of type `content-type:multipart/form-data`
data, with a field `image` containing the image binary data).

E.g. using `curl`:

`curl -X POST -F "image=@/path/to/image.jpg" http://localhost:5000/orient > path/to/new/image.jpg`

#### Restful API using Docker
Build the docker image by running `docker build -t <TAG> .` inside the project root and start the container using
`docker start -d -p 5000:5000 <TAG>`.


### Running Tests
Clone the repo and run `python -m tests` from the project root.

#### Accuracy
Accuracy was tested using the *Faces 1999* dataset from 
[vision.caltech.edu](http://www.vision.caltech.edu/html-files/archive.html). Each of the 450, correctly oriented
images were rotated by `90`, `180` and `270` degrees, resulting in 1800 images in 4 possible orientations.

Predicting orientation on this dataset resulted in an overall accuracy of __~96%__

__Confusion Matrix:__

```
    p/t    down    left    right   up
    down   446     9       7       34
    left   1       416     1       1 
    right  1       24      441     2
    up     2       1       1       413
```
More investigation is needed to determine why some orientations perform better than others.

The accuracy test can be performed by running `python -m tests accuracy` from the project root. The required
data set will be downloaded automatically and prepared for testing.


### Some Notes

96% isn't optimal for the tested dataset, but this is just a proof of concept and definitely not an optimal approach to this problem. For example, it would probably
make more sense to predict image orientation by analyzing the angle between both eyes (and maybe nose).

The first model (which detects faces and draws a rectangle around them) could be skipped, if we can be sure that the
image already contains a cropped face.

In addition, further face analysis would probably be made easier if we not just fix the overall image orientation, but also
align the face properly (with both eyes laying on a straight horizontal line). Maybe I'll add this later.