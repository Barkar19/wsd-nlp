import corpus2
import npsemrel.ml.features.feature_i as fi

class PosBetweenFeature(fi.FeatureI):
	'''
	Konkatenacja POSow pomiedzy elementami relacji semantycznej

	Cecha oparta na pracy "Detecting Semantic Relations Between Nominals Using Support 
	Vector Machines and Linguistic-Based Rules"	Isabel Segura-Bedmar, Doaa Samy, 
	Jose L. Martinez-Fernandez, Paloma Martinez
	'''

	def __init__(self, tagset_str = 'nkjp', interp_tag_str = 'interp'):
		'''
		user_decision - decyzja uzytkownika
		tagset - tagset
		interp_tag_str - string tagu interp
		'''
		super(PosBetweenFeature, self).__init__()
		self.tagset = corpus2.get_named_tagset(tagset_str)
		self.interp_tag_str = interp_tag_str

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
		return '%s;%s;POSITIVE;' % (
				self.__token_poses_between_as_str(user_decision, tok_pos), 
				sem_rel)

	def generate_negative_example(self, user_decision):
		tok_pos = user_decision.syntax_relation.tokens_positions() 
		if (user_decision.auto_semantic_relation == None) or \
				(user_decision.auto_semantic_relation != None and \
					user_decision.manual_semantic_relation == None):
						return None
		sem_rel = user_decision.auto_semantic_relation
		return '%s;%s;NEGATIVE;' % (
				self.__token_poses_between_as_str(user_decision, tok_pos), 
				sem_rel)
	
	def generate_header(self):
		return 'pos_between_semrel_elems;semantic_class;pos_neg_example;' 

	def __token_poses_between(self, ud, tok_pos_e1, tok_pos_e2):
		if abs(tok_pos_e2 - tok_pos_e1) == 1:
			return None
		tok_pos_concat = ''.join(
				(self.__get_str_pos_for_token(ud, tok_position) \
					if self.__get_str_pos_for_token(ud, tok_position) != self.interp_tag_str else '') \
					for tok_position in xrange(tok_pos_e1 + 1, tok_pos_e2))
		return None if len(tok_pos_concat) == 0 else tok_pos_concat

	def __token_poses_between_as_str(self, ud, tok_pos):
		return self.__token_poses_between(ud, min(tok_pos), max(tok_pos))

	def __get_str_pos_for_token(self, ud, tok_pos):
		'''
		Metoda taka sama jak w features.syntax.pos
		XXX: Moze dodac jakas wspolna klase?
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]
		return self.tagset.tag_to_string(
				token.get_preferred_lexeme(self.tagset).tag()).split(':')[0]
