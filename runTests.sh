#!/bin/bash

cd wosedon/wosedon/wosedon

python evaluation-kpwr.py -i idx.txt -r results.txt -p precision.txt -rc recall.txt -d remote.ini
