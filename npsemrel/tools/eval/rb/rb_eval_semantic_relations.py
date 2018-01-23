# -*- coding: utf-8 -*-
'''
Narzedzie do oceny relacji semantycznych wydobytych za pomoca regulowego podejscia

python \
		rb_eval.py \
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
	desc = 'Ocena wykrytych relacji semantycznych - podejscie regulowe'

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


def show_window_relations(np_adjp_phrase, out_dirs):
	'''
	Zwraca liste nowych/niewykrytych relacji w postaci;
	[
		[[poz1, poz2], 'NAZWA']
		...
		[[poz2, poz3, poz6], 'NAZWA']
	]

	Kazda z relacji semantycznych ma kierunek zgodny z kolejnoscia wystepowania pozycji
	tej relacji w liscie opisujacej jedna relacje. Mianowicie:

	[[poz2, poz3, poz6], 'NAZWA] rozwijane jest do postaci:
	poz2 -> [poz3, poz6] NAZWA


	[[poz1, poz2], 'NAZWA'] rozwiniete jest do
	poz1 -> poz2 NAZWA

	Czyli pierwszy element staje sie glowa relacji semantycznej

	'''
	print 40 * '- '
	print ' '.join(
			(str(i) + ':' +
				np_adjp_phrase.annotated_sentence().tokens()[s].orth_utf8())
				for i, s in enumerate(np_adjp_phrase.segments()))
	print ''
	print 'Dostepne relacje:'
	for v, k in ev.rel_available_dict.iteritems():
		print v, ' - ', k
	print 20 * '  - '
	print 'Podaj po kropce kolejne elementy relacji i po znaku rownosci numer relacji, np. 1->2.3=5'
	print 'Kolejne relacje oddzielaj od siebie srednikiem, np. 1->2.3=5; 2<-3=6; 1->2.3'
	relations = raw_input(':')

	if len(relations) < 2:
		return []

	rel_spl = relations.strip().split(';')
	ret_rel = []
	for rel in rel_spl:
		rel_items = []
		rel_name = ''

		if rel.find('=') != -1:
			rel, rel_name = rel.split('=')
			rel_name  = ev.rel_available_dict[int(rel_name)]

		if rel.find('->') != -1:
			r1 = rel.split('->')[0]
			r2 = rel.split('->')[1].split('.')
			rel_items = [r1] + r2
		elif rel.find('<-') != -1:
			r1 = rel.split('<-')[1]
			r2 = rel.split('<-')[0].split('.')
			rel_items = r2 + [r1]
		else:
			rel_items = [int(r) for r in rel.split('.')]
		rel_items = [int(r) for r in rel_items]
		ret_rel.append([rel_items, rel_name])
	return ret_rel

def show_window_additional_relations(np_adjp_phrase, phr_str, out_dirs):
	'''
	-> jezeli nieywkryta jest para/trojka/relacja semantyczna:
		user_decision.correct_pair_triple = False
		user_decision.incorrect_auto_relation = False
		user_decision.auto_semantic_relation = None
		user_decision.manual_semantic_relation = choose_semantic_relation(...)
	'''
	relations = []
	other_relations = raw_input('[?] Czy znajduja sie inne, nieznalezione relacje skladniowe lub semantyczne (t/n)?')
	if other_relations.upper() == 'T':
		relations = show_window_relations(np_adjp_phrase, out_dirs)
	for rel_items, rel_name in relations:
		srel = syntx_rel.SyntaxRelation(np_adjp_phrase, rel_items)
		user_decision = ev.SingleResult(srel)
		user_decision.correct_pair_triple = False
		user_decision.incorrect_auto_relation = False
		user_decision.auto_semantic_relation = None
		user_decision.manual_semantic_relation = rel_name
		save_eval_result(user_decision, out_dirs)

def choose_semantic_relation(semrel_dict):
	print 'Podaj numer prawidlowej relacji i potwierdz enterem:'
	for v, k in semrel_dict.iteritems():
		print v, ' - ', k
	rel_num = raw_input(':')
	return semrel_dict[int(rel_num.strip())]

def simple_dump(rule_point_str, syntax_relation, semantic_relation, wcc_op_cfg_file, only_gen_rel):
	if not only_gen_rel:
		print ''
		print 'Analizowane zdanie i fraza: '
		print ' '.join(tok.orth_utf8() for tok in syntax_relation.np_adjp_phrase().annotated_sentence().tokens())
		print ' '.join((str(i) + ':' +
					syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[s].orth_utf8())
					for i, s in enumerate(syntax_relation.np_adjp_phrase().segments()))
		print ''
		print 80 * '-'
		print ' '.join(
				(syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[s].orth_utf8()
					) for s in syntax_relation.np_adjp_phrase().segments())
	print ''

	for i, tok_pos in enumerate(syntax_relation.tokens_positions()):
		s = syntax_relation.np_adjp_phrase().segments()[tok_pos]
		if i == 0:
			print '[ %s ]' % syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[s].orth_utf8(),
			# sprawdz kierunek strzalki...
			if str(rule_point_str) == '7':
				print ' ~> [',
			else:
				print ' <~ [',
		else:
			print syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[s].orth_utf8(),
	print ']'

	if semantic_relation != None:
		is_right_side = None
		# Domyslnie WCCL dodaje kolejne numerki do nazw operatorow, zatem usuwam ten numerek
		# W rb/options.py zmieniam nazwy operatorow na male, takze nazwe relacjie zmieniam rowniez na male
		sem_rel_name = semantic_relation[0 : semantic_relation.rfind('-')].lower()
		for i, tok_pos in enumerate(syntax_relation.tokens_positions()):
			s = syntax_relation.np_adjp_phrase().segments()[tok_pos]
			if i == 0:
				print '[ %s ]' % syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[s].orth_utf8(),
				# sprawdz kierunek strzalki...
				if sem_rel_name in wcc_op_cfg_file.right_side_ops:
					print ' -> [',
				else:
					if sem_rel_name in wcc_op_cfg_file.left_side_ops:
						print ' <- [',
					else:
						print ' BRAK_USTALONEGO_KIERUNKU_DLA_RELACJI'
			else:
				print syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[s].orth_utf8(),
		print '] =', semantic_relation
	print ''


def show_window(rule_point_str, syntax_relation, semantic_relation, wcc_op_cfg_file, phr_str, eval_count, only_gen_rel):
	'''
	Zwraca:
		- obiekt single_result jezeli dokonano oceny
		- None - jezeli zakonczono ocene
		- False - jezeli pominieto dany przyklad

	Funkcja zmienia pola w obiekcie single_result:
		-> jezeli poprawna jest para/trojka oraz poprawna jest wykryta relacja semantyczna:
			user_decision.correct_pair_triple = True
			user_decision.incorrect_auto_relation = False
			user_decision.auto_semantic_relation = sem_rel
			user_decision.manual_semantic_relation = None
		-> jezeli poprawna jest para/trojka oraz niepoprawna jest wykryta relacja semantyczna:
			user_decision.correct_pair_triple = True
			user_decision.incorrect_auto_relation = True
			user_decision.auto_semantic_relation = sem_rel
			user_decision.manual_semantic_relation = choose_semantic_relation(...)
		-> jezeli poprawna jest para/trojka oraz nie zostala wykryta relacja semantyczna a jest:
			user_decision.correct_pair_triple = True
			user_decision.incorrect_auto_relation = False
			user_decision.auto_semantic_relation = None
			user_decision.manual_semantic_relation = choose_semantic_relation(...)
		-> jezeli poprawna jest para/trojka oraz nie ma relacji semantycznej:
			user_decision.correct_pair_triple = True
			user_decision.incorrect_auto_relation = False
			user_decision.auto_semantic_relation = None
			user_decision.manual_semantic_relation = None
		-> jezeli niepoprawna jest para/trojka to wiadomo, ze nie jest poprawna rowniez relacja semantyczna:
			user_decision.correct_pair_triple = False
			user_decision.incorrect_auto_relation = False
			user_decision.auto_semantic_relation = None
			user_decision.manual_semantic_relation = None
	'''

	# jezeli mam kolejna pare/trojke z tej samej frazy, to nie pokazuje co to za fraza...
	if not only_gen_rel:
		os.system('clear')
		print 80 * '='
		print 'Liczba ocenionych par/trojek (fraza %s): %d' %(phr_str, eval_count)
		print 'Menu:'
		print ' p/ENTER - pomin aktualny przyklad, pokaz nastepny przyklad'
		print ' k - zakoncz ocene fraz %s' % (phr_str)
		print 80 * '='

	# pokazuje jaka mam pare/trojke
	simple_dump(rule_point_str, syntax_relation, semantic_relation, wcc_op_cfg_file, only_gen_rel)
	user_decision = ev.SingleResult(syntax_relation)

	# pytanie o poprawnosc relacji semantycznej
	if semantic_relation != None:
		corr_sem_rel = raw_input('[?] Czy wykryta relacja semantyczna jest poprawna (t/n)?')
		if corr_sem_rel != None:
			# poprawna relacja semantyczna - poprawna para/trojka
			if corr_sem_rel.upper() == 'T':
				user_decision.correct_pair_triple = True
				user_decision.incorrect_auto_relation = False
				user_decision.auto_semantic_relation = semantic_relation
				user_decision.manual_semantic_relation = None
				return user_decision
			else:
				# koneic oceny
				if corr_sem_rel.upper() == 'K':
					return None
				# pomijam przyklad
				if corr_sem_rel.upper() == 'P':
					return False
				# zla relacja semantyczna
				if corr_sem_rel.upper() == 'N':
					user_decision.correct_pair_triple = True
					user_decision.incorrect_auto_relation = True
					user_decision.auto_semantic_relation = semantic_relation
					user_decision.manual_semantic_relation = choose_semantic_relation(ev.rel_available_dict)

					# warunek na: niepoprawna relacja semantyczna, bo nieporawna relacja skladniowa
					if user_decision.manual_semantic_relation == ev.rel_available_dict[0]:
						user_decision.correct_pair_triple = False
						user_decision.incorrect_auto_relation = True
						user_decision.auto_semantic_relation = semantic_relation
						user_decision.manual_semantic_relation = None
					return user_decision
				else:
					return False

	# pytanie o popranowsc dwoji/trojki
	user_decision.incorrect_auto_relation = False
	user_decision.auto_semantic_relation = None
	user_decision.manual_semantic_relation = None

	corr_pair_triple = raw_input('[?] Czy wygenerowana para/trojka jest poprawna (t/n)?')
	if corr_pair_triple != None:
		if corr_pair_triple.upper() == 'T':
			user_decision.correct_pair_triple = True
			is_sem_rel = raw_input('[?] Czy dla zadanej pary zachodzi relacja semantyczna (t/n)?')
			if is_sem_rel.upper() == 'T':
				user_decision.manual_semantic_relation = choose_semantic_relation(ev.rel_available_dict)
			return user_decision
		else:
			if corr_pair_triple.upper() == 'K':
				return None
			if corr_pair_triple.upper() == 'P':
				return False
			if corr_pair_triple.upper() == 'N':
				user_decision.correct_pair_triple = False
				return user_decision
			else:
				return False

def save_eval_result(user_decision, out_dirs):
	filename = out_dirs.make_result_filename_based_on_single_result(user_decision)
	out_dirs.save_single_result(filename, user_decision)

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

def exists_in_previous_decisions(np_adjp_phrase, eval_phrases):
	'''
	Sprawdza czy w wynikach mamy juz oceniona fraze...
	'''
	phr_str = np_adjp_phrase.phrase_type()
	snt_id = np_adjp_phrase.sent_id()
	phr_id = np_adjp_phrase.phrase_identifier()
	for e in eval_phrases:
		e_phr_str = e.syntax_relation.np_adjp_phrase().phrase_type()
		e_snt_id = e.syntax_relation.np_adjp_phrase().sent_id()
		e_phr_id = e.syntax_relation.np_adjp_phrase().phrase_identifier()
		if phr_str == e_phr_str and snt_id == e_snt_id and phr_id == e_phr_id:
			return True
	return False

def start_evaluation(phrases, resource, tagset, wccl_ops, wcc_op_cfg_file, phr_str, out_dirs, eval_phrases):
	eval_count = len(eval_phrases)
	syntax_rel_generator = syntx_rel_gen.SyntaxRelationGenerator()

	for np_adjp_phrase in phrases:
		# jezeli juz ocenialem relacje skladniowa dla frazy NP/AdjP to ja pomijam...
		if exists_in_previous_decisions(np_adjp_phrase, eval_phrases):
			continue

		only_gen_rel = False
		gen_rules = []
		for r in syntax_rel_generator.generate_sytax_relations(np_adjp_phrase, resource, tagset):
			gen_rules.append(r)
		rule_count = len(gen_rules)

		for rule_num, (rule_point_str, syntax_relation) in enumerate(gen_rules):
			# jezeli mam wykryta relacje semantyczna, to oceniam ja...
			semantic_relation = None
			user_decision =  show_window(
					rule_point_str, syntax_relation,
					semantic_relation, wcc_op_cfg_file,
					phr_str, eval_count, only_gen_rel)
			if wccl_ops.has_key(rule_point_str):
				semantic_relation = wccl_ops[rule_point_str].run_wccl_operator(tagset, syntax_relation)
			if user_decision == None:
				return
			elif user_decision == False:
				continue
			else:
				eval_count += 1
				save_eval_result(user_decision, out_dirs)
			only_gen_rel = True
		# moze mam niewykryte relacje skladniowe/semantyczne?
		show_window_additional_relations(np_adjp_phrase, phr_str, out_dirs)

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
