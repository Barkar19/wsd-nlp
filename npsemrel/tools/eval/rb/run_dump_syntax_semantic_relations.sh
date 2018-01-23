#!/bin/bash

CORPUS_DIR="./results/corps/kpwr_izolatka/"
INDEX_CHUNKS="index_chunks.txt"

python rb_dump_syntax_semantic_relations.py \
	-w ../../../cfg/ops.ini \
	-d ${CORPUS_DIR} \
	-C ${INDEX_CHUNKS} \
	-q -O 
