import npsemrel.ml.features.feature_i as fi

class F23ElemsFeature(fi.FeatureI):
	'''
	Klasa posrednia dla relacji semantycznych skladajacych sie
	z 2 lub 3 elementow (dla relacji binarnych np. 
		robione przez Pawla
		Markowe czytanie
		czytanie ksiazki
		czytanie przez Marka
	
	Obsluguje generowanie elementow e1,e2,e3 dla zadanej decyzji uzytkownika
	biorac pod uwage przekazana funkcje generujaca

	Posiada wbudowana funkcje odsiewajaca niepoprawne typy relacji 
	(POSITIVE/NEGATIVE) - te, ktore maja wartosc None
	'''

	def __init__(self, str_funct, str_elem):
		'''
		str_funct -  funkcja genrujaca wartosc typu string dla 
		             kazdego elementu relacji
		str_elem - string, ktory bedzie dodawany do 
		           naglowka dla poszczegolnych elementow
		'''
		super(F23ElemsFeature, self).__init__()
		self.__str_function = str_funct
		self.__str_elem = str_elem

	def generate_2_3_elements(self, user_decision):
		'''
		Dla zadanej decyzji uzytkownika generuje elementy e1, e2, e3 
		zgodnie z zadana funkcja generujaca...
		'''
		e1 = e2 = e3 = None
		tok_pos = user_decision.syntax_relation.tokens_positions()

		if len(tok_pos) == 2 or len(tok_pos) == 3:
			e1 = self.__str_function(user_decision, tok_pos[0])
			e2 = self.__str_function(user_decision, tok_pos[1])
			if len(tok_pos) == 3:
				e3 = self.__str_function(user_decision, tok_pos[2])
		else:
			raise NotImplementedError("feature extract data only from "\
					"the two or three-elemets semantic relation")
		return [e1, e2, e3]
	
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
		e1, e2, e3 = self.generate_2_3_elements(user_decision)
		sem_rel = user_decision.auto_semantic_relation \
				if user_decision.auto_semantic_relation else \
					user_decision.manual_semantic_relation \
						if user_decision.manual_semantic_relation else None
		if sem_rel == None:
			return None
		return '%s;%s;%s;%s;POSITIVE;' % (e1, e2, e3, sem_rel)

	def generate_negative_example(self, user_decision):
		if (user_decision.auto_semantic_relation == None) or \
				(user_decision.auto_semantic_relation != None and \
					user_decision.manual_semantic_relation == None):
						return None
		e1, e2, e3 = self.generate_2_3_elements(user_decision)
		sem_rel = user_decision.auto_semantic_relation
		return '%s;%s;%s;%s;NEGATIVE;' % (e1, e2, e3, sem_rel)
	
	def generate_header(self):
		return 'e1%s;e2%s;e3%s;semantic_class;pos_neg_example;' % (
			self.__str_elem, self.__str_elem, self.__str_elem)
