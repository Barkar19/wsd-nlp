'''
Laduje wszystkie wyniki z danego katalogu i wypisuje decyzje podjete przez uzytkownika w formacie:

	plik_idzdania_idfrazy;decyzja;reczna_relacja_semantyczna;automatyczna_relacja_semantyczna;relacja_skladniowa_kolejnosc;relacja_semantyczna_kolejnosc


UWAGA!

Skrypt nalezy uruchamiac z katalogu, w ktorym znajduje sie aplikacja do oceny 
ze wzgledu na przechowywane sciezki do plikow korpusu (w single_result).
Uruchomienie z innego katalogu nie gwarantuje poprawnosci wczytania wynikow.


Przykladowe uruchomienie:
		 python eval_dump.py \
				 -w cfg/ops.ini \
				 -o out/evaluate/zly-kierunek/ \
				 > out/ocena/ocena_ze_zlym_kierunkiem_v2.csv
'''

import sys
import os
import corpus2
from npsemrel.evaluate import evaluate as ev

def make_parser():
	import argparse
	desc = 'Podsumowanie wynikow oceny recznej'
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True)
	parser.add_argument('-o', '--out-directory', dest = 'out_directory', required = True,
			help = 'Katalog wyjsciowy w ktorym zostaly zapisane wyniki oceny')
	return parser

def make_summation_for_evaluations(out_dirs, eval_phrases, wcc_op_cfg_file):
	p_skl_np_sem_r_sem = 0
	p_skl_p_sem = 0
	p_skl_nwyk_sem_r_sem = 0
	p_skl_bez_sem = 0
	np_skl_np_sem = 0
	nwyk_skl_r_skl_r_sem = 0
	np_skl_bez_sem = 0

	print >> sys.stderr, 'Ocena zapisana w katalogu:', out_dirs.output_directory
	print >> sys.stderr, 'Liczba ocenionych fraz:', len(eval_phrases)

	print 'plik_idzdania_idfrazy;decyzja;reczna_relacja_semantyczna;automatyczna_relacja_semantyczna;relacja_skladniowa_kolejnosc;relacja_semantyczna_kolejnosc'

	for single_result in eval_phrases:
		print '%s_%s_%s;' % (
				os.path.basename(single_result.syntax_relation.np_adjp_phrase().filename),
				single_result.syntax_relation.np_adjp_phrase().sent_id(),
				single_result.syntax_relation.np_adjp_phrase().phrase_identifier()),

		if single_result.correct_pair_triple == True:
			if single_result.incorrect_auto_relation == True:
				p_skl_np_sem_r_sem += 1
				print 'pop_sklad_niepop_wykryta_seman_recznie_dodana_seman;',
				print '%s;' % single_result.manual_semantic_relation,
				print '%s;' % single_result.auto_semantic_relation,
				print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),

			else:
				if single_result.auto_semantic_relation != None:
					p_skl_p_sem += 1
					print 'pop_sklad_pop_wykryta_seman;',
					print '%s;' % single_result.manual_semantic_relation,
					print '%s;' % single_result.auto_semantic_relation,
					# sprawdzam czy mam obrocic autmatyczna relacje
					# Domyslnie WCCL dodaje kolejne numerki do nazw operatorow, zatem usuwam ten numerek
					# W rb/options.py zmieniam nazwy operatorow na male, takze nazwe relacjie zmieniam rowniez na male
					semantic_relation = single_result.auto_semantic_relation
					sem_rel_name = semantic_relation[0 : semantic_relation.rfind('-')].lower()
					if sem_rel_name in wcc_op_cfg_file.left_side_ops:
						# zmiana kierunku 
						tokens = single_result.syntax_relation.tokens_positions()
						corr_tokens = [tokens[-1]] + tokens[0 : -1]
						print '%s' % ' '.join(str(t) for t in corr_tokens),
					else:
						print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),
				else:
					if single_result.manual_semantic_relation != None:
						p_skl_nwyk_sem_r_sem += 1
						print 'pop_sklad_niewykryta_seman_recznie_dodana_seman;',
						print '%s;' % single_result.manual_semantic_relation,
						print '%s;' % single_result.auto_semantic_relation,
						print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),
					else:
						p_skl_bez_sem += 1
						print 'pop_sklad_bez_semantycznej;',
						print '%s;' % single_result.manual_semantic_relation,
						print '%s;' % single_result.auto_semantic_relation,
						print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),
		else:
			if single_result.incorrect_auto_relation == True:
				np_skl_np_sem += 1
				print 'niepop_sklad_niepop_semantyczna;',
				print '%s;' % single_result.manual_semantic_relation,
				print '%s;' % single_result.auto_semantic_relation,
				print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),
			else:
				if single_result.manual_semantic_relation != None and single_result.manual_semantic_relation != False:
					nwyk_skl_r_skl_r_sem += 1
					print 'niewyk_sklad_reczna_skladn_reczna_semantyczna;',
					print '%s;' % single_result.manual_semantic_relation,
					print '%s;' % single_result.auto_semantic_relation,
					print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),
				else:
					np_skl_bez_sem += 1
					print 'niepop_sklad_bez_semantycznej;',
					print '%s;' % single_result.manual_semantic_relation,
					print '%s;' % single_result.auto_semantic_relation,
					print '%s;' % ' '.join(str(p) for p in single_result.syntax_relation.tokens_positions()),
		print ''

	print >> sys.stderr, 'Poprawna skladniowa, niepoprawna semantyczna semantyczna, reczna semantyczna:', p_skl_np_sem_r_sem
	print >> sys.stderr, 'Poprawna skladniowa, poprawna semantyczna:', p_skl_p_sem
	print >> sys.stderr, 'Poprawna skladniowa, niewykryta semantyczna, reczna semantyczna:', p_skl_nwyk_sem_r_sem
	print >> sys.stderr, 'Poprawna skladniowa, bez semantycznej:',  p_skl_bez_sem
	print >> sys.stderr, 'Niepoprawna skladniowa, niepoprawna semantyczna:', np_skl_np_sem
	print >> sys.stderr, 'Niewykryta skladniowa, reczna skladniowa, reczna semantyczna:', nwyk_skl_r_skl_r_sem
	print >> sys.stderr, 'Niepoprawna skladniowa, bez semantycznej:', np_skl_bez_sem

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

	phr_strs = ['NP']
	# phr_strs = ['AdjP']

	for phr_str in phr_strs:
		out_dirs = ev.OutputDirs(args.out_directory, phr_str)
		print >> sys.stderr, 'Loading previous results from %s...' %(out_dirs.output_directory),

		eval_phrases = out_dirs.load_evaluated_phrases(tagset)
		print >> sys.stderr, 'Loaded %d results.' % (len(eval_phrases))

		make_summation_for_evaluations(out_dirs, eval_phrases, wcc_op_cfg_file)


if __name__ == '__main__':
	main()


