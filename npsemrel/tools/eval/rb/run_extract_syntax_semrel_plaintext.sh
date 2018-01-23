#!/bin/bash

python rb_extract_syntax_semrel_plaintext.py \
	-w ../../../cfg/ops.ini \
	-q -O \
	-I workdir/corpus.txt
