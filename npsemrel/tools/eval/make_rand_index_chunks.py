'''
Z przekazanego pliku index_chunks tworzy nowy z losowo wybranymi plikami
Liczba plikow, plik wejsciowy i plik wejsciowy podawane sa jako argumenty

Przyklad uruchomienia:

python make_rand_index_chunks.py \
		-i /home/pkedzia/work/corps/nkjp/NKJP-1.0-converted-tag-chunks/index_chunks.txt \
		-o /home/pkedzia/work/corps/nkjp/NKJP-1.0-converted-tag-chunks/index_chunks_rand_100.txt \
		-C 100
'''

import sys
import codecs
import argparse
import random

def make_parser():
	desc = 'Tworzy index_chunks na podstawie przekazanego, z losowo wybranymi plikami'

	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-i', '--input-file', dest = 'input_file', required = True)
	parser.add_argument('-o', '--output-file', dest = 'output_file', required = True)
	parser.add_argument('-C', '--files-count', dest = 'files_count', required = True)

	return parser

def read_files(input_file):
	in_files = []
	with codecs.open(input_file, 'rt', 'utf8') as infile:
		for line in infile:
			in_files.append(line.strip())
	return in_files

def rand_files(files_list, files_count):
	random.shuffle(files_list)
	return files_list[0:files_count]

def save_files(files_list, output_file):
	with codecs.open(output_file, 'wt', 'utf8') as outfile:
		for f in files_list:
			outfile.write("%s\n" % f)

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)

	input_files = read_files(args.input_file)
	files_count = int(args.files_count)

	if len(input_files) < files_count:
		print >> sys.stderr, 'Files count is bigger than the number of files in input index (%d)' % len(input_files)
		exit(1)
	
	output_files = rand_files(input_files, files_count)
	save_files(output_files, args.output_file)


if __name__ == '__main__':
	main()
