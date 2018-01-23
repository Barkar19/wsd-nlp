import corpus2
import npsemrel.ml.features.f23elems as fi

class BaseFeature(fi.F23ElemsFeature):
	'''
	Ekstraktor form bazowych BASE dla elementow relacji semantycznej
	'''

	def __init__(self, tagset_str = 'nkjp'):
		super(BaseFeature, self).__init__(
				self.__get_base_for_token,
				"_base")
		self.tagset = corpus2.get_named_tagset(tagset_str)

	def __get_base_for_token(self, ud, tok_pos):
		'''
		Zwraca forme bazowa tokenu (BASE)

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]
		return token.get_preferred_lexeme(self.tagset).lemma_utf8()
