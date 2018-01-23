import codecs
import os

'''
Dla slowniku ram walencyjnych Debowskiego
Tworzy Pojedyncze slowniki dla poszczegolnych przypadkow z wyrazami do nich nalezacymi
'''

def make_dictionaries(in_file, output_dir):
	begin = False
	end = True

	dictionaries = dict()

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	with codecs.open(in_file) as f:
		for line in f:
			line = line.strip()

			if end and line.find('{') != -1:
				begin = True
				end = False

			if begin:
				word = line[0 : line.find('=>')].replace("'", "")
				# print word

				for in_line in f:
					if in_line.find('}') != -1:
						begin = False
						end = True
						break
					
					# print '\t', [przyp.replace("'", "").strip() for przyp in in_line.split('=>')[0].split(',')]
					for przyp in in_line.split('=>')[0].split(','):
						if in_line.find('sie') != -1:
							for przyp_sie in in_line.split(','):
								if przyp_sie.find('sie') != -1 or len(przyp_sie.strip()) == 0:
									continue
								else:
									przyp_sie = przyp_sie.replace("'", "").strip()
									if przyp_sie.find('+') != -1:
										pref = przyp_sie.split('+')[0]
										przyp_sie = przyp_sie.split('+')[1]
										
										przyp_beg = przyp_sie.find('(')
										przyp_end = przyp_sie.find(')')
										if przyp_beg == -1 or przyp_end == -1:
											continue
										else:
											przyp_sie = przyp_sie[przyp_beg + 1: przyp_end] +'-sie-' + pref
										if not dictionaries.has_key(przyp_sie):
											dictionaries[przyp_sie] = set()
										dictionaries[przyp_sie].add(word)
									else:
										przyp_beg = przyp_sie.find('(')
										przyp_end = przyp_sie.find(')')

										if przyp_beg == -1 or przyp_end == -1:
											continue
										else:
											przyp_sie = przyp_sie[przyp_beg + 1: przyp_end] +'-sie'
										# print '\t', przyp_sie

										if not dictionaries.has_key(przyp_sie):
											dictionaries[przyp_sie] = set()
										dictionaries[przyp_sie].add(word)
						else:
							przyp = przyp.replace("'", "").strip() 
							if przyp.find('(') != -1:
								if przyp.find('+') != -1:
									pref = przyp.split('+')[0]
									przyp = przyp.split('+')[1]
										
									przyp_beg = przyp.find('(')
									przyp_end = przyp.find(')')
									if przyp_beg == -1 or przyp_end == -1:
										continue
									else:
										przyp = przyp[przyp_beg + 1: przyp_end] +'-' + pref
									if not dictionaries.has_key(przyp):
										dictionaries[przyp] = set()
									dictionaries[przyp].add(word)
								else:
									przyp_beg = przyp.find('(')
									przyp_end = przyp.find(')')

									if przyp_beg == -1 or przyp_end == -1:
										continue

									przyp = przyp[przyp_beg + 1 : przyp_end]
									# print '\t', przyp

									if not dictionaries.has_key(przyp):
										dictionaries[przyp] = set()
									dictionaries[przyp].add(word)

	for dict_name, values in dictionaries.iteritems():
		dict_file = 'dict-' + dict_name + '.lex'
		dict_file = os.path.join(output_dir, dict_file)

		print 'Zapisywanie slownika', dict_file
		with codecs.open(dict_file, 'w', 'utf8') as f:
			for v in values:
				f.write('%s\t1\n' %(v.strip().decode('utf8')))


def main():
	input_file = 'Debowski_filtered.txt'
	output_dir = "val-dic"

	make_dictionaries(input_file, output_dir)

if __name__ == '__main__':
	main()
