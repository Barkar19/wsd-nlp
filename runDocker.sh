#!/bin/bash

docker build -t wosedon . -f Dockerfile-ubuntu
docker run -a stdin -a stdout -i -t wosedon

