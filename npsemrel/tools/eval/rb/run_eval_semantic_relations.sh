#!/bin/bash

CORPUS_DIR="/home/blaz/corporas/kpwr-1.1/"
INDEX_CHUNKS="index_chunks.txt"

python rb_eval_semantic_relations.py \
	-c ../../../cfg/rand.ini \
	-w ../../../cfg/ops.ini \
	-d ${CORPUS_DIR} \
	-C ${INDEX_CHUNKS} \
	-q -O \
	-o out/evaluate/ \
	-m 2
