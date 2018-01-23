import sys
import networkx as nx

from npsemrel.carrot.db import db as mydb

def make_parser():
	import argparse
	desc = 'Generator slownikow hiponimmi od zadanego synsetu (od numeru id tego synsetu)'
	parser = argparse.ArgumentParser(description = desc)
	parser.add_argument('-s', '--synset-id', dest = 'synset_id', required = True)
	parser.add_argument('-p', '--part-of-speech', dest = 'part_of_speech', required = True, help = '2 - rzeczownik, ...')
	parser.add_argument('-d', '--db-config-file', dest = 'db_config_file', required = True)
	parser.add_argument('-w', '--wn-graph-file', dest = 'wn_graph_file', 
			default = 'wn_graph_dump.bin', help = 'Plik zrzutu bazy danych.' \
					' Jezeli plik istnieje, jest wczytywany. Jezeli nie istnieje, jest tworzony')
	return parser

def main(argv = None):
	db = mydb.DB()

	parser = make_parser()
	args = parser.parse_args(argv)

	pos_id = int(args.part_of_speech)
	synset_id = int(args.synset_id)
	graph = db.read_write_wn_graph(args.db_config_file, args.wn_graph_file)
	
	print >> sys.stderr, "Szukam hiponimow dla synsetu %d i czesci mowy %d..." % (synset_id, pos_id)

	print 'lemma;domain;length'
	for e in graph:
		length = -1

		# filtruje posy
		if graph.node[e]['pos'] != pos_id:
			continue

		# sprawdzam polaczenie
		try:
			length = nx.dijkstra_path_length(graph, e, synset_id)
		except Exception, e:
			length = -1
			pass

		# jezeli znalazlem polaczenie wtedy je wypisuje 
		if length > -1:
			for lemma in graph.node[e]['lemmas']:
				print '%s;%s;%d' %(lemma, graph.node[e]['domain'], length)

if __name__ == '__main__':
	main()
