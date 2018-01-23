#coding: utf-8
'''
Ekstrator cech z podjetych decyzji
Cechy specyfikowane sa w pliku konfiguracyjnym

Przyklad uruchomienia:

	 python extractor.py  \
			 -c ../../cfg/extractor.ini \
			 -o ../eval/rb/results/out-new/dobry-kierunek/ 
'''

import corpus2

import argparse, os, sys
import ConfigParser

from npsemrel.carrot.db import db 
from npsemrel.rb import options as wccl_options
from npsemrel.evaluate import evaluate as ev

def make_parser():
	desc = 'Ekstrator cech z podjetych decyzji'
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	parser.add_argument('-c', '--extractor-cfg-file', dest = 'extractor_cfg_file_path', required = True)
	parser.add_argument('-o', '--out-directory', dest = 'out_directory', required = True,
			help = 'Katalog wyjsciowy w ktorym zostaly zapisane wyniki oceny')
	return parser

def load_features(cfg_file, eval_phrases):
	'''
	Z zadanego pliku konfiguracyjnego laduje cechy
	'''
	features = []
	config = ConfigParser.RawConfigParser()

	print >> sys.stderr, 'Loading features...'
	with open(cfg_file, 'r') as ini_file:
		config.readfp(ini_file)
		active_features = config.get('features', 'active').split()
		for feature_section in active_features:
			import_str = config.get(feature_section, 'import')
			fearue_str = config.get(feature_section, 'feature')
			print >> sys.stderr, '\tLoading %s...' % (fearue_str[0 : fearue_str.find('(')]),
			exec('import %s' % import_str)
			f = eval('%s.%s' % (import_str, fearue_str), globals(), locals())
			f.set_user_decisions(eval_phrases)
			features.append(f)
			print >> sys.stderr, ' done!'
	return features

def load_root_list_from_file(filename):
	'''
	Laduje z pliku identyfikatory rodzicow slowosieci
	'''
	roots = []
	with open(filename, 'rt') as fin:
		for line in fin:
			roots.append(line.strip())
	return roots

def merge_examples(examples):
	mer_examples = []
	 
	if len(examples) < 1:
		return examples

	ex_size = len(examples[0])
	delimiter = ';'
	
	# labelka kolumny znajduje sie na przedprzedostatniej pozycji po splitowaniu
	# mam aa;a;a;a;LABELKA;POSNEG;
	column_classlabel = -3
	# decyzja POSITIVE/NEGATIVE znajduje sie na przedostaniej pozycji po splitowaniu
	# mam aa;a;a;a;LABELKA;POSNEG;
	column_pos_neg = -2

	# tworze puste przyklady...
	# wielkosc -> ex_size
	for e in examples[0]:
		mer_examples.append('')

	for example in examples:
		if ex_size != len(example):
			print >> sys.stderr, 'Liczba przykladow jest rozna w liscie przykladow!'
			exit(1)
		for ex_num, e in enumerate(example):
			# zawsze na pozycji:
			# 	- przedostatniej mam decyzje POSITIVE/NEGATIVE
			# 	- przedprzedostatniej mam labelke klasy
			attr_columns = [i for i, espl in enumerate(e.split(delimiter)[0 : column_classlabel])]
			spl_example = e.split(delimiter)
			for a_col in attr_columns:
				mer_examples[ex_num] += spl_example[a_col] + ';'
	
	# dopisuje klase oraz pos/neg
	for ex_num, e in enumerate(examples[0]):
		spl_example = e.split(delimiter)
		mer_examples[ex_num] += spl_example[column_classlabel] + ';'
		mer_examples[ex_num] += spl_example[column_pos_neg] 

	return mer_examples

def run_extraction(features):
	pos_examples = []
	neg_examples = []

	for f in features:
		if not f:
			break
		(pos_ex, neg_ex) = f.extract()
		pos_examples.append(pos_ex)
		neg_examples.append(neg_ex)
	
	pos_examples = merge_examples(pos_examples)
	neg_examples = merge_examples(neg_examples)
	
	for pos_example in pos_examples:
		print pos_example
	
	for neg_example in neg_examples:
		print neg_example

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)
	tagset = corpus2.get_named_tagset(args.tagset)
	phr_strs = ['NP']
	for phr_str in phr_strs:
		out_dirs = ev.OutputDirs(args.out_directory, phr_str)
		
		print >> sys.stderr, 'Loading previous results from %s...' %(out_dirs.output_directory),
		eval_phrases = out_dirs.load_evaluated_phrases(tagset)
		print >> sys.stderr, 'Loaded %d results.' % (len(eval_phrases))
		
		print >> sys.stderr, 'Loading features from %s cfg file...' % (args.extractor_cfg_file_path),
		features = load_features(
				args.extractor_cfg_file_path,
				eval_phrases)
		print >> sys.stderr, 'Loaded %d features.' % (len(features))

		print >> sys.stderr, 'Running extraction proces for %s phrase...' % phr_str,
		run_extraction(features)
		print >> sys.stderr, ' done'

if __name__ == '__main__':
	main()
