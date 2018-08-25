import os

import cv2
import dlib
import numpy as np
from random import randint

from . import utils

# Load models at module-level, so that they will be loaded only once, upon module import
FACE_DETECTOR = dlib.get_frontal_face_detector()
LANDMARK_DETECTOR = dlib.shape_predictor(
    os.path.join(os.path.dirname(__file__), 'model', 'shape_predictor_5_face_landmarks.dat')
)


class FaceOrienter(object):
    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            raise FileNotFoundError('File `%s` was not found.' % str(image_path))

        self.img = cv2.imread(image_path)
        self.landmarks, self.n_rotations = self.__detect_faces()

        self.__predicted_orientation = None

    def __detect_faces(self):
        """
        Checks if the supplied image contains a face. If it doesn't, the image will repeatedly be rotated by 90 degrees
        to check for faces again.

        If a face was found, we will then try to find facial landmarks (eye boundaries and nose tip).

        Returns
        -------
            landmarks : numpy.ndarray | None
                The facial landmark coordinates (or None if no face/landmarks could be found)
            n_rotations : int
                The number of rotations performed
        """
        # Convert to grayscale
        img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)

        n_rotations = 0
        face_rects = FACE_DETECTOR(img_gray, 1)

        # If no faces are detected, rotate the image by 90 degrees and try again
        if len(face_rects) == 0:
            for n_rotations in range(1, 4):
                img_gray = utils.rotate_image(img_gray, 90)
                face_rects = FACE_DETECTOR(img_gray)
                if len(face_rects) > 0:
                    break

        # Find landmarks
        landmarks = None
        if len(face_rects) > 0:
            landmarks = utils.dlib_shape_to_np_array(LANDMARK_DETECTOR(img_gray, face_rects[0]))

        return landmarks, n_rotations

    def predict_orientation(self):
        """
        We're going to predict the orientation by analyzing the position of the nose relative to the eyes (while also
        taking into account the number of rotations required for face(s) to be found)

        More specifically, if the nose's x-position is between the left eye's and the right eye's x-position, we can
        assume that the image is either correctly oriented, or upside down. And if in addition to that, the nose's
        y-position is below that of the eyes, we know that it is correctly oriented. We use the same principle for the
        other orientations.

        Returns
        -------
            str
                Predicted orientation (up/down/right/left)
        """
        if self.__predicted_orientation:
            return self.__predicted_orientation

        if self.landmarks is None:  # For now, just return a random orientation if no landmarks were found (not good)
            return ['down', 'right', 'up', 'left'][randint(0, 3)]

        # Get eye and nose points
        eye_l_points = self.landmarks[0:1]
        eye_r_points = self.landmarks[2:3]
        nose_point = self.landmarks[4]

        # Calculate eye center
        eye_l_center = eye_l_points.mean(axis=0).astype(np.int)
        eye_r_center = eye_r_points.mean(axis=0).astype(np.int)

        # Predict orientation
        if eye_l_center[0] >= nose_point[0] >= eye_r_center[0]:
            if nose_point[1] >= (eye_l_center[1] + eye_r_center[1]) / 2:
                orientation = 0
            else:
                orientation = 2
        else:
            if nose_point[0] >= (eye_l_center[0] + eye_r_center[0]) / 2:
                orientation = 3
            else:
                orientation = 1

        # Take the added rotations into account and return the predicted orientation
        # Also store it, so that it doesn't have to be predicted repeatedly
        self.__predicted_orientation = ['down', 'right', 'up', 'left'][(self.n_rotations + orientation) % 4]

        return self.__predicted_orientation

    def fix_orientation(self, save_path):
        """
        Fixes the orientation of the original image and writes the resulting image to disk.

        Parameters
        ----------
        save_path : str
            Path to which the new image should be written
        """
        n_rotations_required = {
            'down': 0,
            'right': 1,
            'up': 2,
            'left': 3
        }[self.predict_orientation()]

        img_fixed = utils.rotate_image(self.img, n_rotations_required * 90)
        cv2.imwrite(save_path, img_fixed)
