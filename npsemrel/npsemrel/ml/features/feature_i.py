import abc

class FeatureI(object):
	'''
	Klasa umozliwiajaca ekstrakcje cechy z przekazanego zbioru odpowiedzi uzytownika
	'''
	__metaclass__ = abc.ABCMeta

	def __init__(self):
		self.usr_dec = None

	def set_user_decisions(self, user_dec):
		'''
		usr_dec - lista decyzji uzytkownika typu npsmerel.evaluate.evaluate.single_result
		'''
		self.user_dec = user_dec

	def user_decisions(self):
		return self.user_dec

	def extract(self):
		'''
		Podstawowa wersja ekstraktora cechy
		Wedruje po wszystkich przykladach 
		i generuje poprawne oraz negatywne przyklady

		Zwraca pare:
		(
			[lista pozytywnych przykladow],
			[lista negatywnych przykladow]
		)
		'''
		pos_examples = [self.generate_header()]
		neg_examples = [self.generate_header()]

		for ud in self.user_decisions():
			pos_examples.append(self.generate_positive_example(ud))
			neg_examples.append(self.generate_negative_example(ud))
		return self.merge_examples(pos_examples, neg_examples)

	@abc.abstractmethod
	def generate_header(self):
		'''
		generuje naglowek dla pozytywnych i negatywnych przykladow
		'''
		return

	@abc.abstractmethod
	def generate_positive_example(self, user_decision):
		'''
		Dla zadanej decyzji uzytkownika tworzy pozytywny przylad uczacy
		'''
		return
	
	@abc.abstractmethod
	def generate_negative_example(self, user_decision):
		'''
		Dla zadanej decyzji uzytkownika tworzy negatywny przylad uczacy
		'''
		return
	
	@abc.abstractmethod
	def merge_examples(self, pos_examples, neg_examples):
		'''
		Tworzy ostateczna postac przykladow uczacych pozytywnych oraz negatywnych
		'''
		return
