#!/bin/bash
trap "exit" INT
if [ -z $1 ]; then
	echo "Choose build type: arch or ubuntu"
	exit
fi

#Download wosedon
wget https://clarin-pl.eu/dspace/bitstream/handle/11321/290/wosedon.7z
#unpack
7z x wosedon.7z

#run docker
systemctl start docker

#build from Dockerfile
docker build -t wosedon-$1 -f Dockerfile-$1 .

#run with 
docker run -a stdin -a stdout -i -t wosedon-$1 /bin/bash



