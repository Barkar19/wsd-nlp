import corpus2
from npsemrel.carrot import resource
import npsemrel.ml.features.f23elems as fi

class FstPredFeature(fi.F23ElemsFeature):
	'''
	Ekstraktor cech typu:
	
	,,czy element jest predykatem pierwszego typu''
	
	dla elementow relacji semantycznej. W kostruktorze przekazywane sa
	zaladowane zasoby (npsemrel.carrot.resources) - dla tej cechy wymagane
	jest zaladowanie predykatow typu pierwszego
	'''

	def __init__(self, fst_type_pred_file, tagset_str = 'nkjp'):
		super(FstPredFeature, self).__init__(
				self.__get_fst_pred_for_token,
				"_fst_pred")
		self.tagset = corpus2.get_named_tagset(tagset_str) 
		self.resources = resource.Resource(self.tagset)
		self.resources.load_fst_type_predicate_dictionary(fst_type_pred_file)

	def __get_fst_pred_for_token(self, ud, tok_pos):
		'''
		Zwraca:
			True - jezeli element jest predykatem typu pierwszego
			False - jezeli element nie jest predykatem typu pierwszego

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy
		'''
		lexeme = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
					ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]
				].get_preferred_lexeme(self.tagset)

		return self.resources.exists_as_first_predicate(lexeme)
