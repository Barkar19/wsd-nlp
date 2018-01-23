#!/bin/bash

PART_OF_SPEECH=2 
SYN_ID=53426

PYTHONIOENCODING=utf8 \
	python main.py \
		-d config/Spock.properties \
		-w db_dump/wn_graph_dump.bin \
		--part-of-speech ${PART_OF_SPEECH} \
		--synset-id ${SYN_ID} > slownik_surowy.txt && \
			cat slownik_surowy.txt | cut -d ';' -f 1 | sed 's/$/\t1/g' > slownik.lex

# PYTHONIOENCODING=utf8 python main.py -d config/Spock.properties -w db_dump/wn_graph_dump.bin --part-of-speech 2 --synset-id 53426
# Zmiana wyjscia na slownik o formacie wejsciowym zgodnym z leksykonami WCCL:
# cat out | cut -d ';' -f 1 | sed 's/$/\t1/g'
