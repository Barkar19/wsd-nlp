import networkx as nx
from npsemrel.carrot.db import db as mdb
import npsemrel.ml.features.semantic.plwn_base as pwnbase

class PlwnrootFeature(pwnbase.PlwnbaseFeature):
	'''
	Dla wektora skaldajacego sie z len(rootlist) elementow
	cecha sprawdza czy skaldniki relacji sa przodkami z ktoryms 
	elementem z glownych galezi slowosieci.

	Dany element wektora symbolizuje identyfikator synsetu, jezeli element
	z relacji semantycznej nalezy (posiada polaczenie) do ktoregos poddrzewa
	z elementow wektora wstawiana jest tam jedynka, jezeli nie, wstawiane jest 0.

	Cecha przyjmuje na wejsciu graf slowosieci (format mer_graph) oraz liste wezlow (id synsetow)
	bedacych wyznacznikami przynaleznosci do poddrzewa (np. w plWordnecie lista bhp)


	Cecha, dla liczby korzeni 5 moze wygladac tak:

	[0, 0, 0, 0, 1] - jakis skladnik (lub skladniki) posiada rodzica w danym poddrzewie
	[1, 0, 0, 1, 0] - dwa (lub wiecej) skladniki sa dzieckami 1go oraz 4go korzenia
	[0, 0, 0, 0, 0] - zaden skladik nie jest dzieckiem zadnego korzenia

	Cecha oparta na pracy "Detecting Semantic Relations Between Nominals Using Support
	Vector Machines and Linguistic-Based Rules" Isabel Segura-Bedmar, Doaa Samy,
	Jose L. Martinez-Fernandez, Paloma Martinez
	'''

	def __init__(self, db_config_file, wngraph_file, rootlist_file):
		super(PlwnrootFeature, self).__init__()
		self.wngraph = \
				mdb.DB().read_write_wn_graph(db_config_file, wngraph_file)
		self.rootlist = self.__load_root_list_from_file(rootlist_file)
	
	def merge_examples(self, pos_examples, neg_examples):
		new_pos_examples = []
		new_neg_examples = []
		for pos_example in pos_examples:
			if pos_example != None:
				new_pos_examples.append(pos_example)
		for neg_example in neg_examples:
			if neg_example != None:
				new_neg_examples.append(neg_example)
		return (new_pos_examples, new_neg_examples)

	def generate_positive_example(self, user_decision):
		sem_rel = user_decision.auto_semantic_relation \
				if user_decision.auto_semantic_relation else \
					user_decision.manual_semantic_relation \
						if user_decision.manual_semantic_relation else None
		if sem_rel == None:
			return None
		return '%s;%s;POSITIVE;' % (self.__make_feature_vector_as_string(user_decision, ';'), sem_rel)
		
	def generate_negative_example(self, user_decision):
		tok_pos = user_decision.syntax_relation.tokens_positions() 
		if (user_decision.auto_semantic_relation == None) or \
				(user_decision.auto_semantic_relation != None and \
					user_decision.manual_semantic_relation == None):
						return None
		sem_rel = user_decision.auto_semantic_relation
		return '%s;%s;NEGATIVE;' % (self.__make_feature_vector_as_string(user_decision, ';'), sem_rel)
	
	def generate_header(self):
		return '%s;semantic_class;pos_neg_example;' % (
				';'.join( ('eroot_%s' % i) for i, e in enumerate(self.rootlist)))
	
	def __load_root_list_from_file(self, rootlist_file):
		'''
		Loads root ids from given filename
		'''
		roots = []
		with open(rootlist_file, 'rt') as fin:
			for line in fin:
				roots.append(line.strip())
		return roots

	def __make_feature_vector_as_string(self, user_decision, delimiter):
		'''
		Konwertuje wektor cech do postaci stringu, np:
		[0, 0, 1, 1, 0] przekonwertuje z delimiterem ';' na string: 0;0;1;1;0
		'''
		return ';'.join( str(i) for i in self.__built_feature_vector(user_decision))
	
	def __built_feature_vector(self, user_decision):
		'''
		Tworzy wektor opisujacy ceche (opis zgodny z opisem klasy)
		'''
		# cala cecha -> [0, ...., 0]
		feature = []

		# przechowuje id synsetow przypisanych do tokenow
		syn_ids = []
		for tokposition in user_decision.syntax_relation.tokens_positions():
			syn_ids.append(self._get_syn_id(tokposition, user_decision))
	
		# sprawdzam czy dany korzen polaczony jest z ktoryms elementem (synsetem)
		for numroot, rid in enumerate(self.rootlist):
			feature.append(0)
			for synid in syn_ids:
				try:
					nx.dijkstra_path_length(self.wngraph, int(rid), int(synid))
					feature[numroot] = 1
					break
				except Exception, e:
					pass
		return feature
