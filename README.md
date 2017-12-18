Building (in main catalog):

docker build -t wosedon . -f Dockerfile-ubuntu 

docker run -a stdin -a stdout -i -t wosedon-ubuntu

cd wosedon/wosedon

wosedon -f ../../input/<file>.ccl
