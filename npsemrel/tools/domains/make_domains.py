from npsemrel.carrot import domains as dom

input_dir = 'operatory/slowniki/'
output_dir = 'operatory/slowniki/'

# input_file = 'rzecz-dziedzina.out.txt'
# output_file = 'fixed-rzecz-dziedzina.csv'

input_file = 'agens/rzeczowniki-agentywne.csv'
output_file = 'fixed-rzeczowniki-agentywne.csv'

with open(output_dir + output_file, 'w') as fw:
	with open(input_dir + input_file, 'r') as f:
		for line in f:
			print line

			spl_line = line.split(';')
			e1 = spl_line[0].strip()
			e2 = spl_line[1].strip()
			e3 = spl_line[2].strip()

			'''
			e3 = spl_line[2].strip()
			e4 = spl_line[3].strip()
			e5 = spl_line[4].strip()
			e6 = spl_line[5].strip()

			dom_2 = e6
			if dom_2.find('domain') == -1:
				dom_2 = int(dom_2)
			if dom.DOMAINS.has_key(dom_2):
				dom_2 = dom.DOMAINS[dom_2]
			'''

			dom_1 = e2
			if dom_1.find('domain') == -1:
				dom_1 = int(dom_1)
			if dom.DOMAINS.has_key(dom_1):
				dom_1 = dom.DOMAINS[dom_1]


			# fw.write('%s;%s;%s;%s;%s;%s\n' % (e1, e2, dom_1, e4, e5, dom_2))
			fw.write('%s;%s;%s\n' % (e1, dom_1,e3));
