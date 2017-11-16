#!/bin/bash
#Download wosedon
wget https://clarin-pl.eu/dspace/bitstream/handle/11321/290/wosedon.7z
#unpack
7z x wosedon.7z

#run docker
systemctl start docker

#build from Dockerfile
docker build -t wosedon .

#run with 
docker run -a stdin -a stdout -i -t wosedon /bin/bash



