#!/bin/bash

cd wosedon/wosedon/wosedon

python evaluation-kpwr.py -i idx_btw.txt -r results_btw.txt -p precision_btw.txt -rc recall_btw.txt -d remote.ini
python evaluation-kpwr.py -i idx_pr.txt -r results_pr.txt -p precision_pr.txt -rc recall_pr.txt -d remote.ini
