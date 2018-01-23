# -*- coding: utf-8 -*-
'''
Wykorzystany do zrobienia zrzutu wszystkich relacji semantycznych w zadanym 
korpusie. Wykorzystywane jest regulowe podejscie. Zrzut robiony jest w formacie:
	
	plik_idzdania_idfrazy;decyzja;reczna_relacja_semantyczna;automatyczna_relacja_semantyczna;relacja_skladniowa_kolejnosc;relacja_semantyczna_kolejnosc

Gdzie reczna_relacja_semantyczna zawszze posiada wartosc None

Przyklad uruchomienia:

python \
		rb_sem_rel_dump.py \
		-c cfg/rand.ini \
		-w cfg/ops.ini \
		-d /home/pkedzia/work/corps/kpwr-disamb-1.1.4-subdir/ \
		-C index_chunks.txt \
		-q \
		-O \
		-m 0 \
		-o out/evaluation 
'''

import sys
import os
import codecs
import random
import corpus2

from npsemrel.rb import wccl_op as wop
from npsemrel.carrot import resource 
from defender import syn_rel as syntx_rel
from defender import deepened_chunker as syntx_rel_gen
from defender import phrase_reader as phreader
from npsemrel.carrot import options as opts
from npsemrel.evaluate import evaluate as ev

def make_parser():
	import argparse
	desc = 'Dla zadanego korpusu, tworzy zrzut relacji semantycznych wykorzystujac regulowe podejscie'
	
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-c', '--config-file', dest = 'config_file', default = 'cfg/rand.ini')

	
	parser.add_argument('-m', '--run-mode', dest = 'run_mode', default = '2', 
			help = 'Tryb uruchomienia generowania: 0-tylko NP, 1-tylko AdjP, 2-NP oraz AdjP')
	
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True) 
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	
	parser.add_argument('-o', '--out-directory', dest = 'out_directory', required = True,
			help = 'Katalog wyjsciowy w ktorym beda zapisywane wyniki oceny')
	
	parser.add_argument('-d', '--corpus-dir', dest = 'corpus_dir', default = '/home/pkedzia/work/corps/kpwr-1.0')
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

	
# -----------------------------------------------------------------------------
def run_eval_np_adjp(
		ann_phr_reader, resource, tagset, corpus_dir, chunks_file, only_continuous, 
		silent, opts, wccl_ops, wcc_op_cfg_file, out_search_file, run_mode,
		an_phr_annot, an_phr_annot_head, phr_str, out_directory):

	phrases = []
	
	# tworze katalogi do zapisu obiektow oceny
	print >> sys.stderr, 'Creating output directories for evaluation %s phrases...' % (phr_str),
	out_dirs = ev.OutputDirs(out_directory, phr_str)
	print >> sys.stderr, 'done'
	
	# laduje ocenione wczesniej frazy...
	print >> sys.stderr, 'Loading previous decisions', 
	eval_phrases = out_dirs.load_evaluated_phrases(tagset)
	print >> sys.stderr, 'done'

	# czytam frazy
	print >> sys.stderr, 'Reading phrases %s... ' % (phr_str),
	for np_adjp_phrase in ann_phr_reader.read_np_adjp_phrases(
			resource, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, only_continuous, silent):
		dirname = os.path.dirname(np_adjp_phrase.filename)
		if len(np_adjp_phrase.agps()) > opts.np_min_agp_count:
			phrases.append(np_adjp_phrase)
	print >> sys.stderr, 'done'

	# zmienaim kolejnosc wczytanych fraz
	print >> sys.stderr, 'Changing sequence of read %d %s phrases...' % (len(phrases), phr_str),
	random.shuffle(phrases)
	print >> sys.stderr, 'done'

	# uruchamiam ocene...
	start_evaluation(phrases, resource, tagset, wccl_ops, wcc_op_cfg_file, phr_str, out_dirs, eval_phrases)

def start_evaluation(phrases, resource, tagset, wccl_ops, wcc_op_cfg_file, phr_str, out_dirs, eval_phrases):
	eval_count = 0
	syntax_rel_generator = syntx_rel_gen.SyntaxRelationGenerator()

	print 'plik_idzdania_idfrazy;decyzja;reczna_relacja_semantyczna;automatyczna_relacja_semantyczna;relacja_skladniowa_kolejnosc;relacja_semantycznosc_kolejnosc'
	for np_adjp_phrase in phrases:
		gen_rules = []
		for r in syntax_rel_generator.generate_sytax_relations(np_adjp_phrase, resource, tagset):
			gen_rules.append(r)
		for rule_num, (rule_point_str, syntax_relation) in enumerate(gen_rules):
			# jezeli mam wykryta relacje semantyczna, to oceniam ja...
			semantic_relation = None
			if wccl_ops.has_key(rule_point_str):
				semantic_relation = wccl_ops[rule_point_str].run_wccl_operator(tagset, syntax_relation)
			# zapisuje
			print '%s_%s_%s;' % (
					os.path.basename(syntax_relation.np_adjp_phrase().filename),
					syntax_relation.np_adjp_phrase().sent_id(),
					syntax_relation.np_adjp_phrase().phrase_identifier()),
			print 'auto_skl_auto_semantyczna_nie_ocenione; None;',
			print '%s;' % semantic_relation,
			# print '%s;' % ' '.join(str(p) for p in syntax_relation.tokens_positions()),
			print '%s;' % sem_rel_as_numbers(semantic_relation, syntax_relation.tokens_positions(), wcc_op_cfg_file),
			print ''

def sem_rel_as_numbers(semantic_relation, tokens, wcc_op_cfg_file):
	'''
	Zwraca stringa w odpowiedniej kolejnosci jako relacja semantyczna
	
	jezeli lewo: to
		Dla: a <- b c
		Dostaniemy: b c a
		
		Dla: c <- a b
		Dostaniemy: a b c
	
	jezeli prawo, to:
		Dla: a b -> c
		Dostaniemy: a b c
	'''
	if semantic_relation == None:
		return ''

	# Domyslnie WCCL dodaje kolejne numerki do nazw operatorow, zatem usuwam ten numerek
	# W rb/options.py zmieniam nazwy operatorow na male, takze nazwe relacjie zmieniam rowniez na male
	sem_rel_name = semantic_relation[0 : semantic_relation.rfind('-')].lower()

	corr_tokens = []
	if sem_rel_name in wcc_op_cfg_file.right_side_ops:
		corr_tokens = tokens
	elif sem_rel_name in wcc_op_cfg_file.left_side_ops:
		corr_tokens = [tokens[-1]] + tokens[0 : -1]
		print >> sys.stderr, 'Odwracam relacje semantyczna:', tokens, 'na', corr_tokens
	else:
		corr_tokens = tokens

	return ' '.join(str(t) for t in corr_tokens)

def run_evaluation(
		ann_phr_reader, res, tagset, corpus_dir, chunks_file, only_continuous, 
		silent, opts, wccl_ops, wcc_op_cfg_file, out_search_file, run_mode, out_directory):
	'''
	Uruchamia ocene NP i/lub AdjP w zaleznosci od trybu uruchomienia
	'''

	# NP
	if run_mode == 0 or run_mode == 2:
		# wczytuje wszystkie frazy NP
		an_phr_annot = ann_phr_reader.NP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.NP_HEAD_ANNOTATION
		run_eval_np_adjp(
				ann_phr_reader, res, tagset, corpus_dir, chunks_file, only_continuous, 
			silent, opts, wccl_ops, wcc_op_cfg_file, out_search_file, run_mode,
			an_phr_annot, an_phr_annot_head, 'NP', out_directory)
	# AdjP
	if run_mode == 1 or run_mode == 2:
		# wczytuje wszystkie frazy AdjP
		an_phr_annot = ann_phr_reader.ADJP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.ADJP_HEAD_ANNOTATION
		run_eval_np_adjp(
				ann_phr_reader, res, tagset, corpus_dir, chunks_file, only_continuous, 
			silent, opts, wccl_ops, wcc_op_cfg_file, out_search_file, run_mode,
			an_phr_annot, an_phr_annot_head, 'AdjP', out_directory)

# -----------------------------------------------------------------------------

def read_cfg_file(cfg_file):
	op = opts.Options(cfg_file)
	op.parse_cfg()
	return op

def load_wccl_operators(cfg_file, tagset):
	from npsemrel.rb import options 
	op_cfg_file = options.Options(cfg_file)
	op_cfg_file.parse_wccl_cfg()
	op_dict = dict()
	for op_name, op_file in op_cfg_file.operators.iteritems():
		print >> sys.stderr, 'Loading operator:', op_name, 'from file:', op_file 
		wccl_ops = wop.WcclOp()
		wccl_ops.load_wccl_operators(op_file, tagset)
		op_dict[op_name] = wccl_ops
	rules_dict = dict()
	for rul_nmb, op_name in op_cfg_file.rules.iteritems():
		print >> sys.stderr, 'Setting operator:', op_name, 'to rule number:', rul_nmb 
		rules_dict[rul_nmb] = op_dict[op_name]
	return [op_cfg_file, rules_dict]

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)

	# ----------------------------------------------------------------------------
	opts = read_cfg_file(args.config_file)
	
	# ----------------------------------------------------------------------------
	corpus_dir = args.corpus_dir
	chunks_file = args.chunk_file
	tagset = corpus2.get_named_tagset(args.tagset)
	ann_phr_reader = phreader.PhraseReader()

	# ----------------------------------------------------------------------------
	[wcc_op_cfg_file, wccl_ops] = load_wccl_operators(args.wccl_op_cfg_file_path, tagset)
	res = resource.Resource(tagset)
	res.load_fst_type_predicate_dictionary(args.fst_type_pred)
	res.load_ger_dict(args.ger_dict)
	res.load_snd_type_predicate_dictionary(args.snd_type_pred)

	run_evaluation(
			ann_phr_reader, res, tagset, corpus_dir, chunks_file, 
			args.only_continuous, args.silent, opts, wccl_ops, wcc_op_cfg_file,
			args.search_model, int(args.run_mode), args.out_directory)

if __name__ == '__main__':
	main()
