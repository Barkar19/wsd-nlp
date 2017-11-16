#!/bin/bash
#install PLWNGraphBuilder
cd ./wosedon/PLWNGraphBuilder/
python2 setup.py install
cd -

#install wosedon
cd ./wosedon/wosedon/
python2 setup.py install
cd -
