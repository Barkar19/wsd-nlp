#!/bin/bash

CORPUS_DIR="./corps/kpwr_izolatka/"
INDEX_CHUNKS="index_chunks.txt"
OUT_RES="out-new/RANLP-2013"

python make_baseline.py \
	-w ../../..cfg/ops.ini \
	-o ${OUT_RES} \
	-d ${CORPUS_DIR} \
	-C ${INDEX_CHUNKS} \
	-q -O 

