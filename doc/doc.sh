#!/bin/bash

[[ -e build ]] && rm -r build
mkdir build
for target in $(ls | grep -v build); do ln -s ../$target build/$target; done
for target in $(ls | grep tex); do ln -s Dyplom.pdf build/${target/tex/pdf}; done
for target in $(ls | grep tex); do ln -s Dyplom.log build/${target/tex/log}; done
cd build
rm Dyplom.pdf
rm Dyplom.log
pdflatex -interaction=nonstopmode $(realpath Dyplom.tex)
bibtex Dyplom.aux
pdflatex -interaction=nonstopmode $(realpath Dyplom.tex)
pdflatex -interaction=nonstopmode $(realpath Dyplom.tex)


