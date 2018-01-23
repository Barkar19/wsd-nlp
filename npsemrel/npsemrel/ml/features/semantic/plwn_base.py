import npsemrel.ml.features.feature_i as fi

class PlwnbaseFeature(fi.FeatureI):
	'''
	Klasa podstawowa dla cech plWordnetowych.
	
	Zawiera metody do:
		- pobierania identyfikatora synsetu dla zadanego tokenu (pozycji tokenu)
	
	Przechowuje nazwe atrybutu elementu dotyczacego id synsetu (sense:ukb:syns_id)
	'''

	def __init__(self):
		super(PlwnbaseFeature, self).__init__()
		self.token_attribute = 'sense:ukb:syns_id'
	
	def _get_syn_id(self, tok_pos, ud):
		'''
		Dla zadanej pozycji tokena, zwraca identyfikator synsetu przypisany do tokenu
		(wziety np. z WSD ukb). Jezeli token nie ma przypisanego id synsetu w metadanych
		zwracany jest wtedy None
		'''
		token = ud.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
				ud.syntax_relation.np_adjp_phrase().segments()[tok_pos]]
		md_ptr = token.get_metadata()
		if md_ptr:
			att_value = md_ptr.get_attribute(self.token_attribute).strip()
			if len(att_value) > 0: 
				return att_value
		return None
