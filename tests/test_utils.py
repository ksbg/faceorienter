import json
import os
from dlib import full_object_detection, rectangle, point
from unittest import TestCase

import cv2
import numpy as np

from faceorienter.faceorienter import utils


class TestUtils(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example_img = cv2.imread(os.path.join(os.path.dirname(__file__), 'res', 'smiley_orig.jpg'))

    def test_dlib_shape_to_np_array_invalid_args(self):
        """Checks behavior if invalid arguments are passed to utils.dlib_shape_to_np_array"""
        invalid_shapes = [
            (1, (TypeError, AttributeError)),  # Not a shape
            ('1', (TypeError, AttributeError)),  # Not a shape
            ([1, 1], (TypeError, AttributeError)),  # Not a shape
            ([], (TypeError, AttributeError)),  # Not a shape
            (None, (TypeError, AttributeError)),  # Not a shape
            (np.array([]), (TypeError, AttributeError)),  # Not a shape
            (np.array([[1, 1], [2, 2]]), (TypeError, AttributeError)),  # Not a shape
        ]

        for arg, err in invalid_shapes:
            self.assertRaises(err, utils.dlib_shape_to_np_array, arg)

    def test_dlib_shape_to_np_array_results(self):
        """Converts a few example dlib shapes (i.e. dlib.full_object_detection objects) to numpy arrays, and checks if
        the result is as expected"""
        dummy_shapes = [
            full_object_detection(rectangle(),
                                  [point(0, 0)]),
            full_object_detection(rectangle(1, 2, 3, 4),
                                  [point(1, 2), point(2, 3), point(3, 4), point(4, 1)]),
            full_object_detection(rectangle(50, 100, 150, 200),
                                  [point(50, 100), point(100, 150), point(150, 200), point(200, 50)])
        ]

        exptected_results = [[[0, 0]],
                             [[1, 2], [2, 3], [3, 4], [4, 1]],
                             [[50, 100], [100, 150], [150, 200], [200, 50]]]

        for shape, result in zip(dummy_shapes, exptected_results):
            self.assertEqual(np.array_equal(utils.dlib_shape_to_np_array(shape), result), True)

    def test_rotate_image_invalid_args(self):
        """Checks behavior if invalid arguments are passed to utils.rotate_image"""
        invalid_image_args = [
            (1, (TypeError, AttributeError)),  # Not a numpy array
            ('1', (TypeError, AttributeError)),  # Not a numpy array
            ([], (TypeError, AttributeError)),  # Not a numpy array
            (None, (TypeError, AttributeError)),  # Not a numpy array
            (np.array([]), ValueError),  # Empty numpy array
            (np.array([1, 1, 1, 1]), ValueError),  # Invalid array dimensions
            (np.array([[1, 1], [1, 1]]), cv2.error)  # Dimensions ok, but not an image
        ]

        invalid_angle_args = [
            ('90', (TypeError, AttributeError)),  # Not a number
            (self, (TypeError, AttributeError)),  # Not a number
            ([90], (TypeError, AttributeError)),  # Not a number
            (None, (TypeError, AttributeError))  # Not a number
        ]

        for arg, err in invalid_image_args:
            self.assertRaises(err, utils.rotate_image, arg, 90)

        for arg, err in invalid_angle_args:
            self.assertRaises(err, utils.rotate_image, self.example_img, arg)

    def test_rotate_image_results(self):
        """Rotates an example image and checks if the resulting array is as expected"""
        with open(os.path.join(os.path.dirname(__file__), 'res', 'expected_rotation_results.json'), 'r') as result_file:
            expected_results = json.load(result_file)

        for angle in (90, 180, 270, 360, 450, 540, 630, 720, 810, 900, 990, 1080):
            angle %= 360
            self.assertEqual(np.array_equal(utils.rotate_image(self.example_img, angle), expected_results[str(angle)]),
                             True)
