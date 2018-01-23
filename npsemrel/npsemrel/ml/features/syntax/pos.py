import corpus2
import npsemrel.ml.features.f23elems as fi

class PosFeature(fi.F23ElemsFeature):
	'''
	Ekstraktor POS dla elementow relacji semantycznej
	'''

	def __init__(self, tagset_str = 'nkjp'):
		super(PosFeature, self).__init__(
				self.__get_str_pos_for_token,
				"_pos")
		self.tagset = corpus2.get_named_tagset(tagset_str)

	def __get_str_pos_for_token(self, ud, tok_pos):
		'''
		Zwraca POS w postaci stringa

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy

		XXX: Moze jakas wspolna nadklasa z pos_between, poniewaz ta metoda jest taka
		     sama jak w pos_between
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]
		return self.tagset.tag_to_string(
				token.get_preferred_lexeme(self.tagset).tag()).split(':')[0]
