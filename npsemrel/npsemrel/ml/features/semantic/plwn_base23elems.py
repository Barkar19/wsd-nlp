import npsemrel.ml.features.f23elems as fi
import npsemrel.ml.features.semantic.plwn_base as pwnbase

class Plwnbase23ElemsFeature(fi.F23ElemsFeature, pwnbase.PlwnbaseFeature):
	'''
	Klasa bazowa dla cech semantycznych opartych o plWordnet.

	W argumencie konstruktora przyjmuje funkcje generujaca stringa, 
	funkcja ta, przyjmuje numer synsetu dla ktorego wydobywana jest cecha.

	metoda __plwnbase23elems_for_token odczytuje dla zadanego tokeny identyfikator 
	synsetu:
		- jezeli token nie ma przypisanych zadnych atrybutow zwracany jest None
		- jezeli token ma przypisany atrynut sense:ukb:syns_id, odczytuje wartosc
			i uruchamia funkcje str_function z odczytana wartoscia
	
	metoda __plwnbase23elems_for_token przekazywana jest jako metoda generujaca
	string do nadklasy cech dwu/trzyelementowych relacji
	
	'''

	def __init__(self, str_function, str_elem_header):

		super(Plwnbase23ElemsFeature, self).__init__(
				self.__plwnbase23elems_for_token,
				str_elem_header)
		self.str_function = str_function

	def __plwnbase23elems_for_token(self, ud, tok_pos):
		'''
		Uruchamiana jest przekazana funkcja (w konstruktorze klasy)
		z odczytanym identyfikatorem synsetu z oznaczenia tokenu

		ud - decyzja uzytkownika
		tok_pos - pozycja tokenu wzgledem poczatku frazy
		'''
		syn_id = self._get_syn_id(tok_pos, ud)
		if syn_id:
			return self.str_function(syn_id)
		return None 
