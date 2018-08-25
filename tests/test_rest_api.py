import os
from tempfile import mktemp
from unittest import TestCase

from faceorienter import FaceOrienter
from faceorienter.server import app, routes


class TestRestAPI(TestCase):
    def test_fix_orientation_via_rest_api(self):
        """Checks if the result of fixing the orientation using the REST API is the same as when fixing it locally"""
        client = app.test_client()
        client.testing = True
        img = os.path.join(os.path.dirname(__file__), 'res', 'gates_up.jpg')

        # Fix orientation locally and store result in memory
        img_tmp = mktemp(suffix=os.path.splitext(img)[1])
        FaceOrienter(img).fix_orientation(img_tmp)
        with open(img_tmp, 'rb') as img_tmp_fp:
            result_local = img_tmp_fp.read()

        # Fix orientation using the REST API
        with open(img, 'rb') as img_fp:
            response = client.post('/orient', content_type='multipart/form-data',
                                   data={'image': (img_fp, 'gates_up.jpg')})

        # Check if equal
        self.assertEqual(result_local, response.data)
