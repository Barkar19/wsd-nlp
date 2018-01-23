import corpus2
from npsemrel.carrot import resource
import npsemrel.ml.features.f23elems as fi

class SndPredFeature(fi.F23ElemsFeature):
	'''
	Ekstraktor cech typu:
	
	,,czy element jest predykatem drugiego typu''
	
	dla elementow relacji semantycznej. W kostruktorze przekazywane sa
	zaladowane zasoby (npsemrel.carrot.resources) - dla tej cechy wymagane
	jest zaladowanie predykatow typu drugiego
	'''

	def __init__(self, snd_type_pred_file, tagset_str = 'nkjp'):
		super(SndPredFeature, self).__init__(
				self.__get_snd_pred_for_token,
				"_snd_pred")
		self.tagset = corpus2.get_named_tagset(tagset_str)
		# self.resources = resources
		self.resources = resource.Resource(self.tagset)
		self.resources.load_snd_type_predicate_dictionary(snd_type_pred_file)

	def __get_snd_pred_for_token(self, ud, tok_pos):
		'''
		Zwraca:
			True - jezeli element jest predykatem typu drugiego
			False - jezeli element nie jest predykatem typu drugiego

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy
		'''
		lexeme = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
					ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]
				].get_preferred_lexeme(self.tagset)

		return self.resources.exists_as_second_predicate(lexeme)
