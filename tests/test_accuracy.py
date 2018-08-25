"""Tests the accuracy using the Helen-1 dataset (from vision.caltech.edu). Automatically downloads and prepares the
dataset (and cleans up afterwords)."""
import os
from pprint import pprint
from shutil import rmtree
from tarfile import TarFile
from tempfile import mktemp, mkdtemp
from urllib import request

import cv2

from faceorienter import FaceOrienter
from faceorienter.utils import rotate_image


class TestAccuracy(object):
    dataset_tar_url = 'http://www.vision.caltech.edu/Image_Datasets/faces/faces.tar'
    dataset_tar_local = mktemp()
    dataset_dir = mkdtemp()

    @classmethod
    def _download_dataset(cls):
        request.urlretrieve(cls.dataset_tar_url, cls.dataset_tar_local)

    @classmethod
    def _prepare_dataset(cls):
        tar = TarFile(cls.dataset_tar_local)
        tar.extractall(cls.dataset_dir)

        # Get rid of non-image files
        for f in os.listdir(cls.dataset_dir):
            if f[-3:] != 'jpg':
                os.remove(os.path.join(cls.dataset_dir, f))

        images = {
            'up': [],
            'down': os.listdir(cls.dataset_dir),
            'left': [],
            'right': []
        }

        for rot_deg, orientation in zip((90, 180, 270), ('left', 'up', 'right')):
            for img_file in images['down']:
                img = cv2.imread(os.path.join(cls.dataset_dir, img_file))
                new_img_file = orientation + '_' + img_file
                cv2.imwrite(os.path.join(cls.dataset_dir, new_img_file), rotate_image(img, rot_deg))
                images[orientation].append(new_img_file)

        return images

    @classmethod
    def _make_predictions(cls, images):
        confusion_matrix = {
            'up': {'up': 0, 'down': 0, 'left': 0, 'right': 0},
            'down': {'up': 0, 'down': 0, 'left': 0, 'right': 0},
            'left': {'up': 0, 'down': 0, 'left': 0, 'right': 0},
            'right': {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        }

        count = 0
        total = len(os.listdir(cls.dataset_dir))
        for actual_class, img_files in images.items():
            for img_file in img_files:
                predicted_class = FaceOrienter(os.path.join(cls.dataset_dir, img_file)).predict_orientation()
                confusion_matrix[predicted_class][actual_class] += 1
                count += 1
                if count % 100 == 0:
                    print('predicted %d out of %d' % (count, total))

        return confusion_matrix

    @classmethod
    def _calculate_accuracy(cls, confusion_matrix):
        total = sum([v for d in confusion_matrix.values() for v in d.values()])

        return (confusion_matrix['up']['up'] + confusion_matrix['down']['down'] + confusion_matrix['left']['left']
                + confusion_matrix['right']['right']) / float(total)

    @classmethod
    def _clean_up(cls):
        os.remove(cls.dataset_tar_local)
        rmtree(cls.dataset_dir)

    @classmethod
    def run(cls):
        print('Downloading dataset to `%s`...' % cls.dataset_tar_local)
        cls._download_dataset()

        print('Extracting dataset to `%s` and creating rotated copies of images...' % cls.dataset_dir)
        images = cls._prepare_dataset()

        print('Starting prediction...')
        confusion_matrix = cls._make_predictions(images)
        accuracy = cls._calculate_accuracy(confusion_matrix)

        print('Confusion Matrix\n' + '-' * 20)
        pprint(confusion_matrix)

        print('\nAccuracy: %f%%' % accuracy)

        cls._clean_up()
