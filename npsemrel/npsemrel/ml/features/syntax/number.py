import corpus2
import npsemrel.ml.features.f23elems as fi

class NumberFeature(fi.F23ElemsFeature):
	'''
	Ekstraktor Liczby dla elementow relacji semantycznej
	'''

	def __init__(self, tagset_str = 'nkjp', mask_symbol = 'nmb'):
		'''
		mask_symbol - depends on the tagset type - for nkjp is 'nmb'
		'''
		super(NumberFeature, self).__init__(
				self.__get_str_number_for_token,
				"_number")
		self.tagset = corpus2.get_named_tagset(tagset_str)
		self.mask = self.tagset.parse_symbol(mask_symbol)

	def __get_str_number_for_token(self, ud, tok_pos):
		'''
		Zwraca liczbe w postaci stringa

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]

		token_str = self.tagset.tag_to_symbol_string(
				token.get_preferred_lexeme(self.tagset).tag().get_masked(self.mask))
		if len(token_str) < 1:
			return None
		return token_str