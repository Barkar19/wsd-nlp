
class SemanticRelaton:
	'''
	Reprezentuje relacje semantyczna

	Przechowuje informacje o relacji skladniowej na podstawie ktorej dana
	relacja semantyczna zostala utworzona oraz o nazwie relacji semantycznej
	'''

	def __ini__(self, syntax_rel, rel_name):
		self.syntax_rel = syntax_rel
		self.rel_name = rel_name
	
	def syntax_relation(self):
		return self.syntax_rel

	def name(self):
		return self.rel_name

