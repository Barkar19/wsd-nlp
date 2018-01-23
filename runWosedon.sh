#!/bin/bash

cd wosedon/wosedon

echo GTBetweenness
wosedon -f ../../t1.ccl >../../btw.xml

echo GTCloseness	
sed -e "s/GTBetweenness/GTCloseness/" -i cfg/wosedon.ini
wosedon -f ../../t1.ccl >../../clw.xml

echo GTKatz
sed -e "s/GTCloseness/GTKatz/" -i cfg/wosedon.ini
wosedon -f ../../t1.ccl >../../ktz.xml

echo GTAuthority
sed -e "s/GTKatz/GTAuthority/" -i cfg/wosedon.ini
wosedon -f ../../t1.ccl >../../aut.xml

echo GTHub
sed -e "s/GTAuthority/GTHub/" -i cfg/wosedon.ini
wosedon -f ../../t1.ccl >../../hub.xml

echo GTEigenvector
sed -e "s/GTHub/GTEigenvector/" -i cfg/wosedon.ini
wosedon -f ../../t1.ccl >../../egv.xml
