#!/bin/bash

for i in `ls *.out` 
do
	echo "Processing ${i}..."
	cat ${i} | sed 's/\t/;/g' >> ${i}.txt
done
