#encoding: utf8
'''
Aplikacja umozliwiajaca wykrywajaca relacje skladniowe oraz semantyczne z przekazanego tekstu.

Na wejscu przyjmuje text w postaci plain textu,
dokonuje analizy skladniowej, taguje tekst i uruchamia aplikacje wydobywajaca relacje skladiowe i semantyczne

echo "Spod autobusu trzeba było wyciągnąć ciało mężczyzny, który zginął w wypadku." | \
		maca-analyse -o ccl morfeusz-nkjp | \
		wcrft -i ccl -o ccl nkjp_s2.ini -d model_nkjp10_wcrft_s2 - | \
		iobber kpwr.ini -d model-kpwr11-H -i ccl -o ccl - > \
		~/test.cll
'''
import os, sys
import subprocess
from time import gmtime, strftime

def make_parser():
	import argparse
	desc = 'Aplikacja umozliwiajaca wykrywajaca relacje skladniowe oraz semantyczne z przekazanego tekstu.'

	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-w', '--wccl-op-cfg-file', dest = 'wccl_op_cfg_file_path', required = True)

	parser.add_argument('-d', '--corpus-dir', dest = 'corpus_dir', required = False)
	parser.add_argument('-C', '--chunk-file', dest = 'chunk_file', required = False)

	parser.add_argument('-t', '--tagset', dest = 'tagset', default = 'nkjp')
	parser.add_argument('-f', '--first-type-predicates', dest = 'fst_type_pred', default = './resources/dictionaries/dict-syn-mpar.lex')
	parser.add_argument('-g', '--first-type-predicates-gerundium', dest = 'ger_dict', default = './resources/dictionaries/dict-gerundium.lex')
	parser.add_argument('-s', '--second-type-predicates', dest = 'snd_type_pred', default = './resources/dictionaries/dict-pred-snd-type.lex')
	parser.add_argument('-O', '--only-continuius', dest = 'only_continuous', action = 'store_true')
	parser.add_argument('-q', '--silent', dest = 'silent', action = 'store_true')

	parser.add_argument('-W', '--workdir', default = './workdir')

	parser.add_argument('-I', '--input-corp-file', dest = 'input_corp_file', required = False, 
			help = 'Opcjonalny plik wejsciowy z tekstem z ktorego maja zostac wydbobyte relacje skladniowe i semantyczne. ' \
					'Jezeli nie podano, tekst bedzie pobierany z konsoli')

	return parser

def make_workdir(workdir_path):
	if not os.path.exists(workdir_path):
		os.makedirs(workdir_path)

def run_rb_run(args):
	make_workdir(args.workdir)

	input_txt = ''
	print 'HE:', args.input_corp_file
	if args.input_corp_file == None:
		input_txt = raw_input("Podaj tekst do analizy: ")
	else:
		with open(args.input_corp_file, 'rt') as incorpfile:
			for line in incorpfile:
				input_txt += line + ' '

	timestamp = strftime("%A-%d-%m-%Y-%H:%M:%S", gmtime())

	index_chunks_filename = '%s-index_chunks.txt' % timestamp
	input_txt_filename = '%s-read.txt' % timestamp
	corpus_filename = '%s-corp.ccl' % timestamp

	read_txt = os.path.join(args.workdir, input_txt_filename)
	out_txt = os.path.join(args.workdir, corpus_filename)
	index_txt = os.path.join(args.workdir, index_chunks_filename)

	with open(read_txt, "wt") as f:
		f.write(input_txt)

	with open(read_txt, "rt") as f:
		maca = subprocess.Popen(
				["maca-analyse", "-o", "ccl", "morfeusz-nkjp"], 
				stdin = f, 
				stdout = subprocess.PIPE)
		wcrft = subprocess.Popen(
				["wcrft", "-i", "ccl", "-o", "ccl", "nkjp_s2.ini", "-d", "model_nkjp10_wcrft_s2", "-"], 
				stdin = maca.stdout, 
				stdout = subprocess.PIPE)
		iobber = subprocess.Popen(
				["iobber", "kpwr.ini", "-d", "model-kpwr11-H", "-i", "ccl", "-o", "ccl", "-"], 
				stdin = wcrft.stdout, 
				stdout = subprocess.PIPE)

		with open(out_txt, "wt") as fout:
			fout.write(iobber.stdout.read())
		with open(index_txt, "wt") as fout:
			fout.write(corpus_filename)
	
	import rb_dump_syntax_semantic_relations
	rb_dump_syntax_semantic_relations.main([
		'-w', args.wccl_op_cfg_file_path,
		'-d', args.workdir,
		'-C', index_chunks_filename,
		'-t', 'nkjp',
		'-O', '-q'])

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)
	run_rb_run(args)
	
if __name__ == '__main__':
	main()
