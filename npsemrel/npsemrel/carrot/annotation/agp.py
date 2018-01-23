# -*- coding: utf-8 -*-

class AgpPhrase:
	'''
	Przechowuje infomacje o frazie AgP:
	 - co jest glowa (numer tokenu bedacego glowa)
	 - co jest predykatem (numer tokenu bedacego predykatem)
	 - segment rozpinajacy fraze AgP
	'''
	def __init__(self):
		# index of agp head
		self.agp_head_idx = None

		# index of first type predicate s of agp
		self.agp_pred_idx_t1 = []

		# index of second type predicate s of agp
		self.agp_pred_idx_t2 = []
		
		# list of indexes in agp
		self.seg = []

		# What prep is? (store preposition)
		self._prep_lexeme = None
	
	def is_pp(self):
		return self._prep_lexeme
	
	def not_is_pp(self):
		return not self._prep_lexeme 

	def prep_lexeme(self):
		return self._prep_lexeme
	
	def prep_str(self):
		return self.prep_lexeme().lemma_utf8()

	def head(self):
		return self.agp_head_idx

	def first_type_predicates(self):
		return self.agp_pred_idx_t1
	
	def second_type_predicates(self):
		return self.agp_pred_idx_t2

	def segments(self):
		return self.seg
