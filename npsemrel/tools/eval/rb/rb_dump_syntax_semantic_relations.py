# -*- coding: utf-8 -*-
'''
Regulowe wydobywanie relacji -> 
	Reguly pisane w WCCLu i uruchamiane dla wybranych par/trojek wyspecyfiowane w cfg/ops.ini

Dla zadanego korpusu wejsciwoego, wydobywa relacje skladiowe oraz relacje semantyczne 
(wykorzystujac podejscie regulowe) i tworzy z nich zrzut w postiaci tekstowej - rozszerzonej

Przklad uruchomienia:

python rb_dump_syntax_semantic_relations.py \
		-q -w cfg/ops.ini \
		-d /home/pkedzia/work/corps/kpwr-disamb-1.1.4 \
		-C index_chunks.txt \
		-O
'''

import sys
import corpus2

from npsemrel.rb import wccl_op as wop
from defender import phrase_reader as phreader
from defender import syn_rel as syntx_rel
from defender import deepened_chunker as syntx_rel_gen
from defender.managers import np_adjp_manager as npadjp_man
from defender.managers import fst_pred_manager as fst_man
from defender.managers import snd_pred_manager as snd_man
from npsemrel.carrot import resource 
from npsemrel.carrot.annotation.dumper import PhraseDumper

def make_parser():
	import argparse
	desc = 'Z zadanego korpusu wydobywa relacje skladiowe i semantyczne - tworzy zrzut w postaci tekstowej'
	
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True)
	parser.add_argument('-d', '--corpus-dir', dest = 'corpus_dir', required = True)
	parser.add_argument('-C', '--chunk-file', dest = 'chunk_file', required = True)
	
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')

	parser.add_argument('-f', '--first-type-predicates', dest = 'fst_type_pred', 
			default = './resources/dictionaries/dict-syn-mpar.lex')
	parser.add_argument('-g', '--first-type-predicates-gerundium', dest = 'ger_dict', 
			default = './resources/dictionaries/dict-gerundium.lex')
	parser.add_argument('-s', '--second-type-predicates', dest = 'snd_type_pred', 
			default = './resources/dictionaries/dict-pred-snd-type.lex')
	
	parser.add_argument('-O', '--only-continuius', dest = 'only_continuous', action = 'store_true')

	parser.add_argument('-q', '--silent', dest = 'silent', action = 'store_true')
	parser.add_argument('-S', '--stat-only', dest = 'stat_only', action = 'store_true')
	return parser

def show_ann_stats(ann_phr_reader, res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, only_continuous, silent):
	ann_phr_count = 0
	agp_count = 0
	pp_count = 0
	for np_adjp_phrase in ann_phr_reader.read_np_adjp_phrases(
			res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, only_continuous, silent):
		ann_phr_count += 1
		if not silent:
			print ' '.join((str(i) + ':' + t.orth_utf8()) for i, t in enumerate(np_adjp_phrase.syntax_relation.tokens()))
			print '=> ' + an_phr_annot + ':',
			print np_adjp_phrase.segments()
			print '[' + an_phr_annot_head + ' ]',
			print np_adjp_phrase.head()
		for agp in np_adjp_phrase.agps():
			if agp.is_pp():
				pp_count += 1
			else:
				agp_count += 1
			if not silent:
				print ' ~>> AgP:',
				print agp.segments()
				print '  [HEAD AgP]', agp.head()

		if not silent:
			print 40 * '%'
			print 'H  : ',
			for agp_s in range(0, len(np_adjp_phrase.segments())):
				print np_adjp_phrase.is_agp_head_at(agp_s), ' ',
			print ''
			print 'P1 : ',
			for agp_s in range(0, len(np_adjp_phrase.segments())):
				print np_adjp_phrase.is_pred_type1_at(agp_s), ' ',
			print ''
			print 'P2 : ',
			for agp_s in range(0, len(np_adjp_phrase.segments())):
				print np_adjp_phrase.is_pred_type2_at(agp_s), ' ',
			print ''
			print 'SZ : ',
			for agp_s in range(0, len(np_adjp_phrase.segments())):
				print np_adjp_phrase.is_szer_at(agp_s, tagset, res), ' ',
			print ''
			print 40 * '%'

	print 'Liczba fraz ' + an_phr_annot  + ' :', ann_phr_count
	print 'Liczba fraz PP:', pp_count
	print 'Liczba fraz AgP:', agp_count
	print 60 * '*'

def load_wccl_operators(cfg_file, tagset):
	'''
	Zwraca slownik postaci:

	"nazwa_operaotra" obiekt_utworzony_na_podstawie_pliku_cfg
	'''
	from npsemrel.rb import options 
	op_cfg_file = options.Options(cfg_file)

	# tworze mape:
	# 	operatrow (op_cfg_file.operators):
	# 		op_name, op_file
	# 	regul (op_cfg_file.rules):
	# 		rul_nmb, op_name
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

	return rules_dict

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)

	# ----------------------------------------------------------------------------
	corpus_dir = args.corpus_dir
	chunks_file = args.chunk_file
	tagset = corpus2.get_named_tagset(args.tagset)

	# ----------------------------------------------------------------------------
	ann_phr_reader = phreader.PhraseReader()
	syntax_rel_generator = syntx_rel_gen.SyntaxRelationGenerator()
	res = resource.Resource(tagset)

	# ----------------------------------------------------------------------------
	wccl_ops = load_wccl_operators(args.wccl_op_cfg_file_path, tagset)

	# load dictionaries for first-type-predicate
	res.load_fst_type_predicate_dictionary(args.fst_type_pred)
	# load gerundium dictionary
	res.load_ger_dict(args.ger_dict)
	# load dictionaries for first-type-predicate
	res.load_snd_type_predicate_dictionary(args.snd_type_pred)

	# ----------------------------------------------------------------------------
	if args.stat_only:
		an_phr_annot = ann_phr_reader.NP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.NP_HEAD_ANNOTATION
		show_ann_stats(ann_phr_reader, res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, args.only_continuous, args.silent)
		# ----------------------------------------------------------------------------
		an_phr_annot = ann_phr_reader.ADJP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.ADJP_HEAD_ANNOTATION
		show_ann_stats(ann_phr_reader, res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, args.only_continuous, args.silent)
	else:
		# ----------------------------------------------------------------------------
		# NP:
		# Liczba fraz chunk_np : 8569
		# Liczba fraz AgP: 14019
		an_phr_annot = ann_phr_reader.NP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.NP_HEAD_ANNOTATION
		for np_adjp_phrase in ann_phr_reader.read_np_adjp_phrases(
				res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, args.only_continuous, args.silent):

			# dump frazy:
			npadjpman = npadjp_man.NpAdjpManager(np_adjp_phrase)
			fstman = fst_man.FirstTypePredManager(np_adjp_phrase) 
			sndman = snd_man.SecondTypePredManager(np_adjp_phrase)
			dump = PhraseDumper(npadjpman, fstman, sndman)
			dump.dump_phrase(tagset, 2)

			for (rule_point_str, syntax_relation) in syntax_rel_generator.generate_sytax_relations(np_adjp_phrase, res, tagset):
				
				# wyswietlam relacje skladniowa....
				phr_len_syntax_rel = 'pary'
				if len(syntax_relation.tokens_positions()) == 3:
					phr_len_syntax_rel = 'trojki'
				rel_tokens_as_str = ', '.join(str(t) for t in syntax_relation.tokens_positions())
				print ''
				print '%s. Relacja dla %s (OD - DO): <%s>:' % (rule_point_str, phr_len_syntax_rel, rel_tokens_as_str)

				# relacja semantyczna
				if wccl_ops.has_key(rule_point_str):
					sem_rel_name = wccl_ops[rule_point_str].run_wccl_operator(tagset, syntax_relation)
					if sem_rel_name != None:
						print '\t%s' % sem_rel_name
				else:
					print >> sys.stderr, 'Cannot find operator for rule:', rule_point_str
		# ----------------------------------------------------------------------------
		# AdjP:
		# Liczba fraz chunk_adjp : 563
		# Liczba fraz AgP: 1422
		an_phr_annot = ann_phr_reader.ADJP_ANNOTATION
		an_phr_annot_head = ann_phr_reader.ADJP_HEAD_ANNOTATION
		for np_adjp_phrase in ann_phr_reader.read_np_adjp_phrases(
				res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, args.only_continuous, args.silent):

			# dump frazy:
			npadjpman = npadjp_man.NpAdjpManager(np_adjp_phrase)
			fstman = fst_man.FirstTypePredManager(np_adjp_phrase) 
			sndman = snd_man.SecondTypePredManager(np_adjp_phrase)
			dump = PhraseDumper(npadjpman, fstman, sndman)
			dump.dump_phrase(tagset, 2)

			for (rule_point_str, syntax_relation) in syntax_rel_generator.generate_sytax_relations(np_adjp_phrase, res, tagset):

				# wyswietlam relacje skladniowa....
				phr_len_syntax_rel = 'pary'
				if len(syntax_relation.tokens_positions()) == 3:
					phr_len_syntax_rel = 'trojki'
				rel_tokens_as_str = ', '.join(str(t) for t in syntax_relation.tokens_positions())
				print ''
				print '%s. Relacja dla %s (OD - DO): <%s>:' % (rule_point_str, phr_len_syntax_rel, rel_tokens_as_str)

				# relacja semantyczna
				if wccl_ops.has_key(rule_point_str):
					sem_rel_name = wccl_ops[rule_point_str].run_wccl_operator(tagset, syntax_relation)
					if sem_rel_name != None:
						print '\t%s' % sem_rel_name
				else:
					print >> sys.stderr, 'Cannot find operator for rule:', rule_point_str

if __name__ == '__main__':
	main()
