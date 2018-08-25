FROM python:3.6-slim-stretch

COPY . /app
WORKDIR /app

RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    pkg-config \
    libopencv-dev \
    python-opencv \
    python3-dev \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*

RUN pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT python -m faceorienter.server

