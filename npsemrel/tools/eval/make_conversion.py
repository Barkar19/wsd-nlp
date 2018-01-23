'''
Konwertuje wyniki oceny miedzy roznymi wersjami npsemrel

aby konwersja zadzialala miedzy wersjami npsemrel-v.01 a starszym masterem trzeba:
	dodac do .bashrc

	export PYTHONPATH="/home/`whoami`/work/projects/npsemrel":${PYTHONPATH}
	export PYTHONPATH="/home/`whoami`/work/projects/npsemrel_old":${PYTHONPATH}

	w npsemrel_old evaluate.py trzeba zmienic w load_evaluated_phrases
		single_results.append(sres)
	na: 
		single_results.append((sres, eval_file))
'''

import sys
import os
import corpus2
# tak ma zaostac!!
from evaluate import evaluate as ev

def make_parser():
	import argparse
	desc = 'Konwersja wynikow oceny do nowej wersji aplikacji'
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True)
	parser.add_argument('-o', '--out-directory', dest = 'out_directory', required = True,
			help = 'Katalog wyjsciowy w ktorym zostaly zapisane wyniki oceny')
	parser.add_argument('-O', '--out-directory-new-format', dest = 'out_directory_new_format', required = True,
			help = 'Katalog wyjsciowy w ktorym beda zapisane wyniki oceny w nowym formacie')
	return parser

def load_wccl_cfg_file(cfg_file):
	# tak ma zostac!!
	from rb import options
	op_cfg_file = options.options(cfg_file)
	op_cfg_file.parse_wccl_cfg()
	return op_cfg_file

def run_conversion(phrases_old_format, dir_path_new_format):
	from npsemrel import evaluate as evnew
	from npsemrel.evaluate import evaluate as evnew
	from npsemrel.carrot.relations import syn_rel as srelnew
	from npsemrel.carrot.annotation import np_adjp as newnpadjp
	from npsemrel.carrot.annotation import agp as newagp
	
	for o in phrases_old_format:
		oldres = o[0]
		oldfilename = o[1]

		old_syntax = oldres.syntax_relation
		old_np_adjp = old_syntax.np_adjp_phrase()

		new_syntax = srelnew.syntax_relation(None, None)
		new_syntax._np_adjp_phrase = newnpadjp.NpAdjpPhrase(
				old_np_adjp.ann_sent,
				old_np_adjp.phrase_bound,
				old_np_adjp._tagset,
				old_np_adjp.filename,
				old_np_adjp._phrase_identifier,
				old_np_adjp._sent_id,
				old_np_adjp._phrase_type)
		new_syntax._np_adjp_phrase.ann_head = old_np_adjp.ann_head
		new_syntax._np_adjp_phrase._is_countinuous = old_np_adjp._is_countinuous
		new_syntax._np_adjp_phrase.cas_mask = old_np_adjp.cas_mask
		new_syntax._np_adjp_phrase.prep_mask = old_np_adjp.prep_mask

		new_agps = []
		for agp in old_np_adjp.agp_phr:
			nagp = newagp.AgpPhrase()
			nagp.agp_head_idx = agp.agp_head_idx
			nagp.agp_pred_idx_t1 = agp.agp_pred_idx_t1
			nagp.agp_pred_idx_t2 = agp.agp_pred_idx_t2
			nagp.seg = agp.seg
			nagp._prep_lexeme = agp._prep_lexeme
		new_syntax._np_adjp_phrase.agp_phr = new_agps

		new_syntax.tok_positions = old_syntax.tok_positions
		new_syntax.ann_sentence = old_syntax.ann_sentence
		
		newres = evnew.SingleResult(new_syntax)
		newres.correct_pair_triple = oldres.correct_pair_triple
		newres.incorrect_auto_relation = oldres.incorrect_auto_relation

		newres.manual_semantic_relation = oldres.manual_semantic_relation
		newres.auto_semantic_relation = oldres.auto_semantic_relation
		
		# save newres into dir_path_new_format
		newodirs = evnew.OutputDirs(dir_path_new_format, old_np_adjp._phrase_type)
		newfilename = os.path.join(dir_path_new_format, os.path.basename(oldfilename))
		newodirs.save_single_result(newfilename, newres)

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)
	tagset = corpus2.get_named_tagset(args.tagset)
	wcc_op_cfg_file = load_wccl_cfg_file(args.wccl_op_cfg_file_path)

	phr_strs = ['NP']
	# phr_strs = ['AdjP']

	for phr_str in phr_strs:
		out_dirs = ev.output_dirs(args.out_directory, phr_str)
		print >> sys.stderr, 'Loading previous results from %s...' %(out_dirs.output_directory),

		eval_phrases = out_dirs.load_evaluated_phrases(tagset)
		print >> sys.stderr, 'Loaded %d results.' % (len(eval_phrases))

		run_conversion(eval_phrases, args.out_directory_new_format)


if __name__ == '__main__':
	main()
