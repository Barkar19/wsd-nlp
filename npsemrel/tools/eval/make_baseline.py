'''
Laduje wszystkie wyniki z danego katalogu i wypisuje decyzje podjete przez 
uzytkownika w zadanym formacie. Dodatkowo dla kazdej decyzji losuje relacje 
sematyczna (jej nazwe) z okreslonym pradopodobienstwem wylosowania relacji.

	plik_idzdania_idfrazy;decyzja;relacja_semantyczna_decyzji;relacja_semantyczna_losowa


UWAGA!

Skrypt nalezy uruchamiac z katalogu, w ktorym znajduje sie aplikacja do oceny 
ze wzgledu na przechowywane sciezki do plikow korpusu (w single_result).
Uruchomienie z innego katalogu nie gwarantuje poprawnosci wczytania wynikow.


Przykladowe uruchomienie:
		 python eval_dump.py \
				 -w cfg/ops.ini \
				 -o out/evaluate/zly-kierunek/ \
				 > out/ocena/relacje_semantyczne_baseline.csv
'''

import sys
import os
import corpus2
import random

from npsemrel.evaluate import evaluate as ev

from npsemrel.carrot import resource
from npsemrel.carrot import phrase_reader as phreader
from npsemrel.carrot.relations import syn_rel as syntx_rel
from npsemrel.carrot.relations import deepened_chunker as syntx_rel_gen
from npsemrel.carrot.annotation.managers import np_adjp_manager as npadjp_man

def make_parser():
	import argparse
	desc = 'Tworzenie baselinu dla relacji semantycznych'

	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True)
	parser.add_argument('-o', '--out-directory', dest = 'out_directory', required = True,
			help = 'Katalog wyjsciowy w ktorym zostaly zapisane wyniki oceny')

	parser.add_argument('-d', '--corpus-dir', dest = 'corpus_dir', required = False)
	parser.add_argument('-C', '--chunk-file', dest = 'chunk_file', required = False)
	parser.add_argument('-f', '--first-type-predicates', dest = 'fst_type_pred',\
			default = './resources/dictionaries/dict-syn-mpar.lex')
	parser.add_argument('-g', '--first-type-predicates-gerundium', dest = 'ger_dict',
			default = './resources/dictionaries/dict-gerundium.lex')
	parser.add_argument('-s', '--second-type-predicates', dest = 'snd_type_pred',
			default = './resources/dictionaries/dict-pred-snd-type.lex')

	parser.add_argument('-O', '--only-continuius', dest = 'only_continuous', action = 'store_true')
	parser.add_argument('-q', '--silent', dest = 'silent', action = 'store_true')

	return parser

def make_baseline_for_loaded_relations(out_dirs, eval_phrases, wcc_op_cfg_file):
	print >> sys.stderr, 'Ocena zapisana w katalogu:', out_dirs.output_directory
	print >> sys.stderr, 'Liczba ocenionych fraz:', len(eval_phrases)

	print 'plik;decyzja;relacja_semantyczna;relacja_semantyczna_losowa'
	for single_result in eval_phrases:
		if single_result.correct_pair_triple == True:
			if single_result.incorrect_auto_relation == True:
				print '%s_%s_%s;' % (
						os.path.basename(single_result.syntax_relation.np_adjp_phrase().filename),
						single_result.syntax_relation.np_adjp_phrase().sent_id(),
						single_result.syntax_relation.np_adjp_phrase().phrase_identifier()),
				print 'pop_sklad_niepop_wykryta_seman_recznie_dodana_seman;',
				print '%s;' % single_result.manual_semantic_relation,
				print '%s' % rand_semantic_relation()
			else:
				if single_result.auto_semantic_relation != None:
					print '%s_%s_%s;' % (
							os.path.basename(single_result.syntax_relation.np_adjp_phrase().filename),
							single_result.syntax_relation.np_adjp_phrase().sent_id(),
							single_result.syntax_relation.np_adjp_phrase().phrase_identifier()),
					print 'pop_sklad_pop_wykryta_seman;',
					print '%s;' % single_result.auto_semantic_relation,
					print '%s' % rand_semantic_relation()
				else:
					if single_result.manual_semantic_relation != None:
						print '%s_%s_%s;' % (
								os.path.basename(single_result.syntax_relation.np_adjp_phrase().filename),
								single_result.syntax_relation.np_adjp_phrase().sent_id(),
								single_result.syntax_relation.np_adjp_phrase().phrase_identifier()),
						print 'pop_sklad_niewykryta_seman_recznie_dodana_seman;',
						print '%s;' % single_result.manual_semantic_relation,
						print '%s' % rand_semantic_relation()
					else:
						pass
						'''
						print 'pop_sklad_bez_semantycznej;',
						print '%s;' % single_result.manual_semantic_relation,
						print '%s;' % single_result.auto_semantic_relation
						'''
		else:
			if single_result.incorrect_auto_relation == True:
				pass
				'''
				print 'niepop_sklad_niepop_semantyczna;',
				print '%s;' % single_result.manual_semantic_relation,
				print '%s;' % single_result.auto_semantic_relation
				'''
			else:
				if single_result.manual_semantic_relation != None and single_result.manual_semantic_relation != False:
					print '%s_%s_%s;' % (
							os.path.basename(single_result.syntax_relation.np_adjp_phrase().filename),
							single_result.syntax_relation.np_adjp_phrase().sent_id(),
							single_result.syntax_relation.np_adjp_phrase().phrase_identifier()),
					print 'niewyk_sklad_reczna_skladn_reczna_semantyczna;',
					print '%s;' % single_result.manual_semantic_relation,
					print '%s' % rand_semantic_relation()
				else:
					pass
					'''
					print 'niepop_sklad_bez_semantycznej;',
					print '%s;' % single_result.manual_semantic_relation,
					print '%s;' % single_result.auto_semantic_relation
					'''

def rand_semantic_relation():
	# rozklad klas zgodny z prawdopodobienstwem ich wystapienia
	'''
	sem_rels = {
			'OTHER' : [0.7954, ' INNA RELACJA SEMANTYCZNA'],
			'PROTO_AGENT' : [0.0175, 'SUBIEKT'],
			'PROTO_PATIENT'	: [0.0821, ' OBIEKT'],
			'INSTRUMENT' : [0.0054, ' INSTRUMENT'],
			'MATERIAL' : [0.0013, ' MATERIAL'],
			'PURPOSE'	: [0.0256, ' PRZEZNACZENIE'],
			'LOCATION' : [0.0188, 'MIEJSCE'],
			'SP_MERONYMY' : [0.0000, 'MERONIMIA-MIEJSCA'],
			'TIME' : [0.0040, 'CZAS'],
			'T_MERONYMY' : [0.0027, ' CZAS-MERONIMIA'],
			'ATTRIBUTE' : [0.0215, 'WLASCIWOSC'],
			'FAMILY' : [0.0027, 'RODZINA'],
			'ORDER' : [0.0081, 'KOLEJNOSC'],
			'QUANTITY' : [0.0148, 'ILOSC']
		}
	scale = 10000
	'''
	
	# rownomierny rozklad klas:
	prob_whole = 0.0714
	sem_rels = {
			'OTHER' : [prob_whole, 'INNA RELACJA SEMANTYCZNA'],
			'PROTO_AGENT' : [prob_whole, 'SUBIEKT'],
			'PROTO_PATIENT'	: [prob_whole, 'OBIEKT'],
			'INSTRUMENT' : [prob_whole, 'INSTRUMENT'],
			'MATERIAL' : [prob_whole, 'MATERIAL'],
			'PURPOSE'	: [prob_whole, 'PRZEZNACZENIE'],
			'LOCATION' : [prob_whole, 'MIEJSCE'],
			'SP_MERONYMY' : [prob_whole, 'MERONIMIA-MIEJSCA'],
			'TIME' : [prob_whole, 'CZAS'],
			'T_MERONYMY' : [prob_whole, 'CZAS-MERONIMIA'],
			'ATTRIBUTE' : [prob_whole, 'WLASCIWOSC'],
			'FAMILY' : [prob_whole, 'RODZINA'],
			'ORDER' : [prob_whole, 'KOLEJNOSC'],
			'QUANTITY' : [prob_whole, 'ILOSC']
		}
	scale = 10000

	sem_rel_list = []
	for rel_dict_name, rel_value in sem_rels.iteritems():
		rel_count = int(rel_value[0] * scale)
		sem_rel_list.extend([rel_dict_name] * rel_count)
	return sem_rels[sem_rel_list[random.randint(0, len(sem_rel_list) - 1)]][1]

def make_baseline_for_syntax(ev_phrases, tagset, args):
	'''
	dla wczytanych decyzji uzytkownika z relacjami semantycznymi, 
	odszukuje tych relacji skladniowych rozpoznanych automatycznie,
	ktorych nie ma w obrebie relacji semantycznych

	ev_phrases - wczytane wczesniej, ocenione, relacje semantyczne
	tagset - tagset
	args - przekazane argumenty z linii wywloania
	'''

	corpus_dir = args.corpus_dir
	chunks_file = args.chunk_file
	ann_phr_reader = phreader.phrase_reader()
	syntax_rel_generator = syntx_rel_gen.syntax_relation_generator()
	res = resource.Resource(tagset)
	res.load_fst_type_predicate_dictionary(args.fst_type_pred)
	res.load_ger_dict(args.ger_dict)
	res.load_snd_type_predicate_dictionary(args.snd_type_pred)

	for phr_str, sem_rel_answers in ev_phrases.iteritems():
		an_phr_annot = ''
		an_phr_annot_head = ''

		if phr_str.lower() == 'np':
			an_phr_annot = ann_phr_reader.NP_ANNOTATION
			an_phr_annot_head = ann_phr_reader.NP_HEAD_ANNOTATION
		elif phr_str.lower() == 'adjp':
			an_phr_annot = ann_phr_reader.ADJP_ANNOTATION
			an_phr_annot_head = ann_phr_reader.ADJP_HEAD_ANNOTATION
		else:
			print >> sys.stderr, 'Skipped %s type of phrases!' % (phr_str)
			continue

		for np_adjp_phrase in ann_phr_reader.read_np_adjp_phrases(
				res, tagset, corpus_dir, chunks_file, an_phr_annot, an_phr_annot_head, args.only_continuous, args.silent):
			if is_in_same_phrase(np_adjp_phrase, sem_rel_answers):
				for (rule_point_str, syntax_relation) in syntax_rel_generator.generate_sytax_relations(np_adjp_phrase, res, tagset):
					tok_pos = syntax_relation.tokens_positions()
					if not is_syntax_relation_in_ansewers(sem_rel_answers, syntax_relation):
						print '%s_%s_%s;%s;%s;%s' % (
									os.path.basename(syntax_relation.np_adjp_phrase().filename),
									syntax_relation.np_adjp_phrase().sent_id(),
									syntax_relation.np_adjp_phrase().phrase_identifier(),
									'skl_niewystepujaca_w_sem',
									'BRAK',
									rand_semantic_relation())

def is_in_same_phrase(np_adjp_phrase, sem_rel_answers):
	for answer in sem_rel_answers:
		an_npadjp = answer.syntax_relation.np_adjp_phrase()
		if an_npadjp.sent_id() == np_adjp_phrase.sent_id() and \
				an_npadjp.phrase_identifier() == np_adjp_phrase.phrase_identifier() and \
				an_npadjp.filename == np_adjp_phrase.filename:
					return True
	return False

def is_syntax_relation_in_ansewers(sem_rel_answers, syntax_relation):
	'''
	Sprawdza czy w odpowiedzach znajduje sie odpowiedz, 
	ktora obejmuje wskazana relacje skladniowa

	Zwraca: True jezeli tak, w przeciwnym razie False
	'''
	npadjp = syntax_relation.np_adjp_phrase()
	tok_pos = syntax_relation.tokens_positions()
	for answer in sem_rel_answers:
		an_npadjp = answer.syntax_relation.np_adjp_phrase()
		if an_npadjp.sent_id() == npadjp.sent_id() and \
				an_npadjp.phrase_identifier() == npadjp.phrase_identifier() and \
				an_npadjp.filename == npadjp.filename:
					an_tok_pos = answer.syntax_relation.tokens_positions()
					if an_tok_pos == an_npadjp:
						return True

	return False

def load_wccl_cfg_file(cfg_file):
	from npsemrel.rb import options
	op_cfg_file = options.Options(cfg_file)
	op_cfg_file.parse_wccl_cfg()
	return op_cfg_file


def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)
	tagset = corpus2.get_named_tagset(args.tagset)
	wcc_op_cfg_file = load_wccl_cfg_file(args.wccl_op_cfg_file_path)

	# phr_strs = ['NP', 'AdjP']
	phr_strs = ['NP']
	ev_phrases = dict()

	for phr_str in phr_strs:
		out_dirs = ev.OutputDirs(args.out_directory, phr_str)
		print >> sys.stderr, 'Loading previous results from %s (%s phrase)...' %(out_dirs.output_directory, phr_str),
		ev_phrases[phr_str] = out_dirs.load_evaluated_phrases(tagset)

		print >> sys.stderr, 'Loaded %d results.' % (len(ev_phrases[phr_str]))
		print >> sys.stderr, 'Making baseline for  %s phases.' % (phr_str)
		make_baseline_for_loaded_relations(out_dirs, ev_phrases[phr_str], wcc_op_cfg_file)
	
	# ----------------------------------------------------------------------------
	if args.corpus_dir and args.chunk_file:
		make_baseline_for_syntax(ev_phrases, tagset, args)

if __name__ == '__main__':
	main()


