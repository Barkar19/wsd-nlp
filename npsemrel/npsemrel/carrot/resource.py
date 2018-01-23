# -*- coding: utf-8 -*-

import sys
import codecs

class Resource:
	def __init__(self, tagset):
		# dictioary of first type predicate: 
		# 	key: lemma, 
		# 	value: domain
		self.fst_type_preds = dict()

		# dictioary of second type predicates: 
		# 	key: lemma_noun, 
		# 	value: lemma_verb
		self.snd_type_preds = dict()

		# dictionary of gerundiums:
		# 	zżywać      -> zżywanie
		# 	zobojętnić  -> zobojętnienie
		# 	zobojętniać -> zobojętnianie
		self.ger_dict = dict()
		
		# tagset
		self.tagset = tagset

		# ppas and pact mask
		self.ppas_mask = tagset.parse_symbol('ppas')
		self.pact_mask = tagset.parse_symbol('pact')

		# szeregowe....
		# bądź też, 
		self._series = ["a", "albo", "ani", "bądź", "czy", "i", "jak", "lub", "oraz", ","]
	
	def series(self):
		return self._series
	
	def first_type_predicates(self):
		return self.fst_type_preds
	
	def second_type_predicates(self):
		return self.snd_type_preds

	def gerundium_dictionary(self):
		return self.ger_dict

	# ----------------------------------------------------------------------------
	def is_ppas(self, lexeme):
		ppas_lex_mask = lexeme.tag().get_masked(self.ppas_mask)
		return ppas_lex_mask == self.ppas_mask

	def is_pact(self, lexeme):
		pact_lex_mask = lexeme.tag().get_masked(self.pact_mask)
		return pact_lex_mask == self.pact_mask

	def is_ppas_or_pact(self, lexeme):
		return self.is_ppas(lexeme) or self.is_pact(lexeme)
	
	# ----------------------------------------------------------------------------

	def exists_as_first_predicate(self, lexeme):
		return self.first_type_predicates().has_key(lexeme.lemma_utf8().lower())
	
	def value_of_first_predicate(self, lexeme):
		if not self.exists_as_first_predicate(lexeme):
			return None
		return self.first_type_predicates()[lexeme.lemma_utf8().lower()]
	
	def is_first_type_predicate(self, lexeme):
		return self.is_ppas_or_pact(lexeme) or self.exists_as_first_predicate(lexeme)
	
	def is_first_type_predicate_str(self, str_lexeme):
		return self.first_type_predicates().has_key(str_lexeme)
	
	# ----------------------------------------------------------------------------

	def exists_as_second_predicate(self, lexeme):
		return self.second_type_predicates().has_key(lexeme.lemma_utf8().lower())
	
	def value_of_second_predicate(self, lexeme):
		if not self.exists_as_second_predicate(lexeme):
			return None
		return self.second_type_predicates()[lexeme.lemma_utf8().lower()]

	def is_second_type_predicate(self, lexeme):
		return self.exists_as_second_predicate(lexeme)
	
	# ----------------------------------------------------------------------------
	
	def exists_as_gerundium(self, lexeme):
		return self.gerundium_dictionary().has_key(lexeme.lemma_utf8().lower())
	
	def value_of_gerundium(self, lexeme):
		if not self.exists_as_gerundium(lexeme):
			return None
		return self.gerundium_dictionary()[lexeme.lemma_utf8().lower()]
	
	# ----------------------------------------------------------------------------
	def load_fst_type_predicate_dictionary(self, file_pah_syn_mpar, verbose = False):
		if verbose:
			print >> sys.stderr, 'Loading first type predicate dictionary...',
		with codecs.open(file_pah_syn_mpar, 'r') as f:
			for line in f:
				line = line.strip()
				k_lemma, v_domain = line.split()
				self.fst_type_preds[k_lemma] = v_domain
		if verbose:
			print >> sys.stderr, ' done'

	def load_snd_type_predicate_dictionary(self, file_pah, verbose = False):
		if verbose:
			print >> sys.stderr, 'Loading second type predicate dictionary...',
		with codecs.open(file_pah, 'r') as f:
			for line in f:
				line = line.strip()
				k_lemma, v_domain = line.split('\t')
				self.snd_type_preds[k_lemma] = v_domain
		if verbose:
			print >> sys.stderr, ' done'
	
	def load_ger_dict(self, file_path_ger, verbose = False):
		if verbose:
			print >> sys.stderr, 'Loading gerundium dictionary...',
		with codecs.open(file_path_ger, 'r') as f:
			for line in f:
				k_ger, v_subst = line.strip().split()
				self.ger_dict[k_ger] = v_subst
		if verbose:
				print >> sys.stderr, ' done'
