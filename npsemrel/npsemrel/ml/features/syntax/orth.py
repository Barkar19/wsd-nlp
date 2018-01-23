import npsemrel.ml.features.f23elems as fi

class OrthFeature(fi.F23ElemsFeature):
	'''
	Ekstraktor ORTH dla elementow relacji semantycznej
	'''

	def __init__(self):
		super(OrthFeature, self).__init__(
				self.__get_orth_for_token,
				"_orth")

	def __get_orth_for_token(self, ud, tok_pos):
		'''
		Zwraca ORTH tokenu

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]
		return token.orth_utf8()
