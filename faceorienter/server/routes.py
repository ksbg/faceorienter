import os
from tempfile import mktemp

from flask import request

from faceorienter import FaceOrienter
from faceorienter.server import app


@app.route('/orient', methods=['POST'])
def orient():  # TODO return proper errors
    files = request.files

    if 'image' in files:
        f = files['image']
        img_ext = os.path.splitext(f.filename)[1]
        img_tmp = mktemp(suffix=img_ext)
        f.save(img_tmp)
        fo = FaceOrienter(img_tmp)

        img_fixed_tmp = mktemp(suffix=img_ext)
        fo.fix_orientation(img_fixed_tmp)
        img_new_bytes = open(img_fixed_tmp, 'rb').read()

        os.remove(img_tmp)
        os.remove(img_fixed_tmp)

        return img_new_bytes
    else:
        return ''
