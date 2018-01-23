from ltlearn.io import  arff

import ltcore
import sys

print >> sys.stderr, 'Loading LexCSD matrix...'
# m = ltcore.io.matrix.load_matrix('npsemrel.tar.bz')
m = ltcore.io.matrix.load_matrix('npsemrel-coarse.tar.bz')

print >> sys.stderr, 'Converting to arff...'
# arff.sparse_matrix_to_arff('npsemrel.arff', m)
arff.sparse_matrix_to_arff('npsemrel-coarse.arff', m)
