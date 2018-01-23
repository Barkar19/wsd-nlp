import corpus2
import npsemrel.ml.features.feature_i as fi

class PosWindowFeature(fi.FeatureI):
	'''
	Konkatenacja POSow pomiedzy elementami relacji semantycznej

	Cecha oparta na pracy "Detecting Semantic Relations Between Nominals Using Support 
	Vector Machines and Linguistic-Based Rules"	Isabel Segura-Bedmar, Doaa Samy, 
	Jose L. Martinez-Fernandez, Paloma Martinez
	'''

	def __init__(self, tagset_str, interp_tag_str, left_window_size, right_window_size):
		'''
		user_decision - decyzja uzytkownika
		tagset - tagset
		interp_tag_str - string tagu interp
		'''
		super(PosWindowFeature, self).__init__()
		self.tagset = corpus2.get_named_tagset(tagset_str)
		self.interp_tag_str = interp_tag_str
		self.left_window_size = left_window_size
		self.right_window_size = right_window_size

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
				self.__token_poses_window_as_str(user_decision, tok_pos), 
				sem_rel)

	def generate_negative_example(self, user_decision):
		tok_pos = user_decision.syntax_relation.tokens_positions() 
		if (user_decision.auto_semantic_relation == None) or \
				(user_decision.auto_semantic_relation != None and \
					user_decision.manual_semantic_relation == None):
						return None
		sem_rel = user_decision.auto_semantic_relation
		return '%s;%s;NEGATIVE;' % (
				self.__token_poses_window_as_str(user_decision, tok_pos), 
				sem_rel)
	
	def generate_header(self):
		return 'pos_window_semrel_left;pos_window_semrel_right;semantic_class;pos_neg_example;' 

	def __get_left_side(self, tok_pos_e, ud):
		# dodawaje do lsity a pozniej odwracam kolejnosc tej listy bo inaczej
		# jest zla kolejnosc w liscie! bo dodaje od konca do poczatku
		strlist = []
		proc_tok = 0
		for tok_pos in range(tok_pos_e - 1, -1, -1):
			if proc_tok >= self.left_window_size:
				break
			else:
				tok_str = self.__get_str_pos_for_token(ud, tok_pos)
				if tok_str == self.interp_tag_str:
					continue
				else:
					strlist.append(tok_str)
					proc_tok += 1
		# dopelniam z lewej Nonami
		strlist.reverse()
		return ''.join('None' for i in range(proc_tok, self.left_window_size)
				) + ''.join(posstr for posstr in strlist) 

	def __get_right_side(self, tok_pos_e, ud):
		right_str = ''
		proc_tok = 0
		# operuje wewnatrz frazy, nie zdania!!
		# dlatego dopelnianie jest do frazy a nie zdania!!
		for tok_pos in range(
				tok_pos_e + 1, len(ud.syntax_relation.np_adjp_phrase().segments())):
			if proc_tok >= self.right_window_size or \
					tok_pos >= len(ud.syntax_relation.np_adjp_phrase().segments()):
				break
			else:
				tok_str = self.__get_str_pos_for_token(ud, tok_pos)
				if tok_str == self.interp_tag_str:
					continue
				else:
					right_str += tok_str
					proc_tok += 1
		# dopelniam z prawej
		return right_str + \
				''.join('None' for i in range(proc_tok, self.right_window_size)) 

	def __token_poses_window(self, ud, tok_pos_e1, tok_pos_e2):
		return '%s;%s' % (
				self.__get_left_side(tok_pos_e1, ud), 
				self.__get_right_side(tok_pos_e2, ud))

	def __token_poses_window_as_str(self, ud, tok_pos):
		return self.__token_poses_window(ud, min(tok_pos), max(tok_pos))

	def __get_str_pos_for_token(self, ud, tok_pos):
		'''
		Metoda taka sama jak w features.syntax.pos
		XXX: Moze dodac jakas wspolna klase?
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]
		return self.tagset.tag_to_string(
				token.get_preferred_lexeme(self.tagset).tag()).split(':')[0]
