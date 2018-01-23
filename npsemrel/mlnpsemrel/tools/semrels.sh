#!/bin/bash

mdr=npsemrel_`date +%Y-%m-%d-%H%M%S`
mkdir ${mdr}
mv npsemrel-coarse.arff npsemrel-coarse.tar.gz npsemrel.csv npsemrel.tar.bz npsemrel-spl npsemrel.arff $mdr

fextor \
  -b ~/dokumenty/Projekty/CLARIN/Kamienie/M24-A12-2015-05-25-kpwr-np_sem_roles/wikinews.idx.org \
  -c ../cfg/npsemrel_sets.ini \
    > npsemrel.csv

python /home/pkedzia/repos/fextor/fextor/fextor/apps/fextor2lexcsd.py \
  -c ../cfg/npsemrel_sets.ini \
  -i npsemrel.csv \
  -o npsemrel.tar.bz \
  -v -l

# python semrels.py

#python  ../fextor/fextor/apps/wsd_split.py -i npsemrel.csv -s ";" -l -v -o npsemrel-spl
#for csv in `ls npsemrel-spl`;
#do
#  python ../fextor/fextor/apps/fextor2lexcsd.py -c npsemrel_sets.ini   -i npsemrel-spl/$csv  -o npsemrel-spl/${csv}.tar.bz -v -l
#done
