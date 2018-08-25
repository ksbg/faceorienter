from setuptools import setup

with open('requirements.txt', 'r') as req_file:
    requirements = req_file.readlines()

setup(
    name='faceorienter',
    version='0.1',
    url='https://github.com/ksbg/faceorienter',
    author='Kevin Baumgarten',
    author_email='kevin@ksbg.io',
    description='A small proof of concept which fixes the orientation of images containing (frontal) faces. Comes with '
                'a RESTful API (for python3)',
    packages=['faceorienter', 'faceorienter.server', 'faceorienter.model'],
    install_requires=requirements,
    python_requires='>=3.3',
    include_package_data=True,
    package_data={'faceorienter.model': ['shape_predictor_5_face_landmarks.dat']}
)