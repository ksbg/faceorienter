import cv2
import numpy as np


def dlib_shape_to_np_array(shape):
    """Converts a dlib shape object (i.e. dlib.full_object_detection) to a numpy array

    Parameters
    ----------
    shape : dlib.full_object_detection
        The shape to be converted

    Returns
    -------
    numpy.ndarray
        The resulting array
    """
    # Init empty array
    arr = np.zeros((shape.num_parts, 2), dtype=np.int)

    # Convert each landmark to a (x, y) tuple
    for i in range(0, shape.num_parts):
        arr[i] = (shape.part(i).x, shape.part(i).y)

    return arr


def rotate_image(image, angle):
    """
    Rotates an image clockwise by performing the following steps:

    1. Extract the dimensions of the image and determine the center
    2. Create the rotation matrix, then extract the sine and cosine from it
    3. Calculate the new dimensions of the image using the rotation matrix's sine and cosine
    4. Correct the rotation matrix and perform the actual rotation

    Parameters
    ----------
    image : numpy.ndarray
        The image to be rotated
    angle : int
        The angle according to which the image should be rotated

    Returns
    -------
    numpy.ndarray
        The rotated image
    """
    # Get Dimensions and find center
    (height, width) = image.shape[:2]
    (centerX, centerY) = (width / 2., height / 2.)

    # Get Rotation Matrix and sine & cosine
    matrix = cv2.getRotationMatrix2D((centerX, centerY), -angle, 1.0)  # Negative angle for clockwise rotation
    cos = np.abs(matrix[0, 0])
    sin = np.abs(matrix[0, 1])

    # Calculate new dimensions
    new_width = int((height * sin) + (width * cos))
    new_height = int((height * cos) + (width * sin))

    # Adjust rotation matrix to take dimension transformation into account
    matrix[0, 2] += (new_width / 2) - centerX
    matrix[1, 2] += (new_height / 2) - centerY

    # Rotate the image and return
    return cv2.warpAffine(image, matrix, (new_width, new_height))
