import codecs, sys, argparse

from npsemrel.carrot.db import db 

'''
Konwerter unitstringow do identyfikatorow synsetow

python unitsstr2synid.py \
		-i unitsstr_list.txt \
		-d eval/rb/cfg/spock.db \
		-o ustr_dict.csv
'''

def make_parser():
	desc = 'Converter plWordnet units strings to synset id'
	parser = argparse.ArgumentParser(description = desc) 
	parser.add_argument('-i', '--input-file', dest = 'input_file', required = True)
	parser.add_argument('-o', '--output-file', dest = 'output_file', required = True)
	parser.add_argument('-d', '--db-cfg-file', dest = 'db_config_file', required = True)
	return parser

def read_list(filename):
	usstrs = []
	with codecs.open(filename, 'rt') as fin:
		for line in fin:
			usstrs.append(line.strip())
	return usstrs

def conver_usstrs2id(usstrs, dbconnection, output_file):
	cursor = dbconnection.cursor()

	with codecs.open(output_file, 'wt') as ofile:
		for usstr in usstrs:
			query = "SELECT id FROM synset WHERE unitsstr = '%s'" % usstr
			cursor.execute(query)
			synid = cursor.fetchone()
			if synid:
				ofile.write('%s;%s\n' % (usstr, synid[0]))
			else:
				print >> sys.stderr, 'Cannot find %s unitsstr in database!' % (usstr)

def main(argv = None):
	parser = make_parser()
	args = parser.parse_args(argv)

	print >> sys.stderr, 'Connecting to DB...',
	dbcon = db.DB()
	dbconnection = dbcon.connect(args.db_config_file)
	if not dbconnection:
		print >> sys.stderr, 'Cannot connect to DB!'
		exit(1)
	print >> sys.stderr, ' done'

	print >> sys.stderr, 'Reading list of unitsstrings...',
	usstrs = read_list(args.input_file)
	print >> sys.stderr, ' done'

	print >> sys.stderr, 'Converting unitsstrings to synset id...',
	conver_usstrs2id(usstrs, dbconnection, args.output_file)
	print >> sys.stderr, ' done'

if __name__ == '__main__':
	main()
