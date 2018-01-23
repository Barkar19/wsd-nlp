#!/bin/bash

python \
	rb_sem_rel_dump.py \
	-c ../../../cfg/rand.ini \
	-w ../../../cfg/ops.ini \
	-d /home/blaz/corporas/kpwr-1.1/ \
	-C index_chunks.txt \
	-q \
	-O \
	-m 0 \
	-o out/evaluation 
