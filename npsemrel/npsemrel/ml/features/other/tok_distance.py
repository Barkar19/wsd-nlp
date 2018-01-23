import npsemrel.ml.features.feature_i as fi

class TokenDistanceFeature(fi.FeatureI):
	'''
	Cecha wskazujaca na odleglosc miedzy dwoma tokenami (elementami relacji
	semantycznej) w zdaniu.
	
	
	Posiada wbudowana funkcje odsiewajaca niepoprawne typy relacji 
	(POSITIVE/NEGATIVE) - te, ktore maja wartosc None
	'''

	def __init__(self):
		'''
		user_decision - decyzja uzytkownika
		'''
		super(TokenDistanceFeature, self).__init__()

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
		tok_pos = user_decision.syntax_relation.tokens_positions() 
		sem_rel = user_decision.auto_semantic_relation \
				if user_decision.auto_semantic_relation else \
					user_decision.manual_semantic_relation \
						if user_decision.manual_semantic_relation else None
		if sem_rel == None:
			return None
		return '%d;%s;POSITIVE;' % (max(tok_pos) - min(tok_pos), sem_rel)

	def generate_negative_example(self, user_decision):
		tok_pos = user_decision.syntax_relation.tokens_positions() 
		if (user_decision.auto_semantic_relation == None) or \
				(user_decision.auto_semantic_relation != None and \
					user_decision.manual_semantic_relation == None):
						return None
		sem_rel = user_decision.auto_semantic_relation
		return '%d;%s;NEGATIVE;' % (max(tok_pos) - min(tok_pos), sem_rel)
	
	def generate_header(self):
		return 'token_distance;semantic_class;pos_neg_example;' 
