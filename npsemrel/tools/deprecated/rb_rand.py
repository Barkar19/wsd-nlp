# -*- coding: utf-8 -*-
'''
python \
		rb_rand.py -c cfg/rand.ini \
		-w cfg/ops.ini \
		-d /home/pkedzia/work/corps/kpwr-disamb-1.1.4-subdir/ \
		-C index_chunks.txt \
		-q -O

Generator losowych fraz adjp/np lub dokumentow je zawierajacych
'''

import sys
import os
import codecs
import random

import corpus2

from rb import wccl_op as wop

from carrot import resource 
from carrot.relations import syn_rel as syntx_rel
from carrot.relations import deepened_chunker as syntx_rel_gen
from carrot import phrase_reader as phreader
from carrot import options as opts
from carrot.annotation.dumper import phrase_dumper

from carrot.annotation.managers import np_adjp_manager as npadjp_man 
from carrot.annotation.managers import fst_pred_manager as fst_man
from carrot.annotation.managers import snd_pred_manager as snd_man

def make_parser():
	import argparse
	desc = 'Generator losowych fraz adjp/np lub dokumentow je zawierajacych'
	
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-c', '--config-file', dest = 'config_file', default = 'cfg/rand.ini')

	
	parser.add_argument('-m', '--run-mode', dest = 'run_mode', default = '2', 
			help = 'Tryb uruchomienia generowania: 0-tylko NP, 1-tylko AdjP, 2-NP oraz AdjP')
	
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True) 
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	
	parser.add_argument('-d', '--corpus-dir', dest = 'corpus_dir', default = '/home/pkedzia/work/corps/kpwr-1.0')
	# parser.add_argument('-d', '--corpus-dir', dest = 'corpus_dir', default = '/home/pkedzia/work/corps/kpwr-disamb-1.1.4')
	parser.add_argument('-C', '--chunk-file', dest = 'chunk_file', default = 'index_chunks.txt')

	parser.add_argument('-f', '--first-type-predicates', dest = 'fst_type_pred', 
			default = './resources/dictionaries/dict-syn-mpar.lex')
	parser.add_argument('-g', '--first-type-predicates-gerundium', dest = 'ger_dict', 
			default = './resources/dictionaries/dict-gerundium.lex')
	parser.add_argument('-s', '--second-type-predicates', dest = 'snd_type_pred', 
			default = './resources/dictionaries/dict-pred-snd-type.lex')
	
	parser.add_argument('-M', '--search-model', dest = 'search_model',
			help = 'Plik wyjsciowy modelu wyszukiwania, jezeli podano to jest wczytywany/zapisywany wynik losowania')
	
	parser.add_argument('-O', '--only-continuius', dest = 'only_continuous', action = 'store_true')
	parser.add_argument('-q', '--silent', dest = 'silent', action = 'store_true')
	
	return parser

def load_wccl_operators(cfg_file, tagset):
	from rb import options 
	op_cfg_file = options.options(cfg_file)
	op_cfg_file.parse_wccl_cfg()
	
	op_dict = dict()
	for op_name, op_file in op_cfg_file.operators.iteritems():
		print >> sys.stderr, 'Loading operator:', op_name, 'from file:', op_file 
		wccl_ops = wop.wccl_op()
		wccl_ops.load_wccl_operators(op_file, tagset)
		op_dict[op_name] = wccl_ops

	rules_dict = dict()
	for rul_nmb, op_name in op_cfg_file.rules.iteritems():
		print >> sys.stderr, 'Setting operator:', op_name, 'to rule number:', rul_nmb 
		rules_dict[rul_nmb] = op_dict[op_name]
	
	return rules_dict

def rand_n_phrases(phrase_list, phrase_count):
	'''
	if len(phrase_list) < phrase_count:
		return phrase_list
	'''

	phr_idx = [x for x in range(0, len(phrase_list))]
	random.shuffle(phr_idx)
	return phr_idx[0 : phrase_count]

def load_rand_history(out_file):
	'''
	Z pliku modelu losowania laduje wylosowane probki
	'''
	rand_history = []
	with codecs.open(out_file, 'r', 'utf8') as f:
		for line in f:
			filename = line.strip()
			phrase = f.readline().strip()
			rand_history.append((filename, phrase))
	return rand_history


def rand_phrases(
		ann_phr_reader, res, tagset, corpus_dir, chunks_file, only_continuous, 
		silent, opts, wccl_ops, out_search_file, run_mode = 2):
	# run_mode = 
	# 	0 - uruchami np
	# 	1 - uruchami adjp
	# 	2 - uruchami np + adjp

	# list of tuples:
	# 	(filename, phrase)
	rand_history = []
	if out_search_file != None:
		rand_history = load_rand_history(out_search_file)

	# NP
	if run_mode == 0 or run_mode == 2:
		print >> sys.stderr, '-' * 80
		phrases = dict()
		an_phr_annot = ann_phr_reader.NP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.NP_HEAD_ANNOTATION
		syntax_rel_generator = syntx_rel_gen.syntax_relation_generator()
		for ann_phrase in ann_phr_reader.read_np_adjp_phrases(
				res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, only_continuous, silent):
			dirname = os.path.dirname(ann_phrase.filename)
			if len(ann_phrase.agps()) > opts.np_min_agp_count:
				if not phrases.has_key(dirname):
					phrases[dirname] = []
				phrases[dirname].append(ann_phrase)
		for k, v in phrases.iteritems():
			phrase_idx = []
			print '\n'
			print 100 * '>'
			print '\t', k,
			for npk, npv in opts.np_phrases.iteritems():
				print npk
				print npv
				print 100 * '~'

				continue
				if k.find(npk) != -1:
					phrase_idx = rand_n_phrases(v, opts.np_phrases[npk])
					print >> sys.stderr,'\t [*] NP:', npk, len(phrase_idx)
					for idx in phrase_idx:

						npadjpman = npadjp_man.np_adjp_manager(np_adjp_phrase) 
						fstman = fst_man.first_type_pred_manager(np_adjp_phrase)
						sndman = snd_man.second_type_pred_manager(np_adjp_phrase)
						dump = phrase_dumper(npadjpman, fstman, sndman)
						dump.dump_phrase(tagset, 1)

						for (rule_point_str, ann_sent) in syntax_rel_generator.generate_sytax_relations(v[idx], res, tagset):
							if wccl_ops.has_key(rule_point_str):
								wccl_ops[rule_point_str].run_wccl_operator(tagset, ann_sent, True)
	
	return
	# AdjP
	if run_mode == 1 or run_mode == 2:
		print >> sys.stderr, '-' * 80
		phrases = dict()
		an_phr_annot = ann_phr_reader.ADJP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.ADJP_HEAD_ANNOTATION
		syntax_rel_generator = syntx_rel_gen.syntax_relation_generator()
		for ann_phrase in ann_phr_reader.read_np_adjp_phrases(
				res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, only_continuous, silent):
			dirname = os.path.dirname(ann_phrase.filename)
			if len(ann_phrase.agps()) > opts.adjp_min_agp_count:
				if not phrases.has_key(dirname):
					phrases[dirname] = []
				phrases[dirname].append(ann_phrase)
		for k, v in phrases.iteritems():
			phrase_idx = []
			print '\n'
			print 100 * '>'
			print '\t', k,
			for npk, npv in opts.adjp_phrases.iteritems():
				if k.find(npk) != -1:
					phrase_idx = rand_n_phrases(v, opts.adjp_phrases[npk])
					print >> sys.stderr,'\t [~] AdjP:', npk, len(phrase_idx)
					for idx in phrase_idx:

						npadjpman = npadjp_man.np_adjp_manager(np_adjp_phrase) 
						fstman = fst_man.first_type_pred_manager(np_adjp_phrase)
						sndman = snd_man.second_type_pred_manager(np_adjp_phrase)
						dump = phrase_dumper(npadjpman, fstman, sndman)
						dump.dump_phrase(tagset, 1)

						for (rule_point_str, ann_sent) in syntax_rel_generator.generate_sytax_relations(v[idx], res, tagset):
							if wccl_ops.has_key(rule_point_str):
								wccl_ops[rule_point_str].run_wccl_operator(tagset, ann_sent, True)

def read_cfg_file(cfg_file):
	op = opts.options(cfg_file)
	op.parse_cfg()
	return op

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)

	# ----------------------------------------------------------------------------
	opts = read_cfg_file(args.config_file)
	
	# ----------------------------------------------------------------------------
	corpus_dir = args.corpus_dir
	chunks_file = args.chunk_file
	tagset = corpus2.get_named_tagset(args.tagset)
	ann_phr_reader = phreader.phrase_reader()

	# ----------------------------------------------------------------------------
	wccl_ops = load_wccl_operators(args.wccl_op_cfg_file_path, tagset)

	res = resource.resource(tagset)
	res.load_fst_type_predicate_dictionary(args.fst_type_pred)
	res.load_ger_dict(args.ger_dict)
	res.load_snd_type_predicate_dictionary(args.snd_type_pred)
	
	rand_phrases(
			ann_phr_reader, res, tagset, corpus_dir, chunks_file, 
			args.only_continuous, args.silent, opts, wccl_ops, 
			args.search_model, int(args.run_mode))

if __name__ == '__main__':
	main()
