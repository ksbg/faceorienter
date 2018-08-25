import os
from tempfile import mktemp
from unittest import TestCase

import cv2

from faceorienter import FaceOrienter


class TestFaceOrienter(TestCase):
    @classmethod
    def setUpClass(cls):
        res_dir = os.path.join(os.path.dirname(__file__), 'res')
        cls.gates_images = {
            'left': os.path.join(res_dir, 'gates_left.jpg'),
            'right': os.path.join(res_dir, 'gates_right.jpg'),
            'up': os.path.join(res_dir, 'gates_up.jpg'),
            'down': os.path.join(res_dir, 'gates_down.jpg'),
        }

    def test_init_invalid_args(self):
        """Checks the behavior when the object is instantiated using invalid arguments"""
        # Try to init the object with non-existing image
        self.assertRaises(FileNotFoundError, FaceOrienter, '/some/non/existing/image.jpg')

        # Try to init the object with a file that is not a valid image
        self.assertRaises(cv2.error, FaceOrienter, __file__)

    def test_init_image_without_face(self):
        """Tests the behavior when an image is supplied that does not contain a face"""
        # Test using an image containing black square (shouldn't fail, but just make a random guess)
        try:
            fo = FaceOrienter(os.path.join(os.path.dirname(__file__), 'res', 'black_square.jpg'))
        except Exception as e:
            self.fail('An exception was raised unexpectedly: \n%s.%s: %s' %
                      (e.__class__.__module__, e.__class__.__name__, str(e)))

        # No landmarks should have been found
        self.assertEqual(fo.landmarks, None)

    def test_predict_orientation(self):
        """Checks if predicting the orientation works using very clear, easy-to-predict, frontal-view portrait images"""

        for orientation, img_path in self.gates_images.items():
            self.assertEqual(orientation, FaceOrienter(img_path).predict_orientation())

    def test_fix_orientation(self):
        """Checks if fixing the orientation works using very clear, easy-to-predict, frontal-view portrait images"""
        for img_path in self.gates_images.values():
            img_tmp = mktemp(suffix=os.path.splitext(img_path)[1])
            FaceOrienter(img_path).fix_orientation(img_tmp)

            # After fixing the orientation, the newly predicted orientation should always be `down`
            # (TODO: not a very good approach)
            self.assertEqual(FaceOrienter(img_tmp).predict_orientation(), 'down')
            os.remove(img_tmp)
