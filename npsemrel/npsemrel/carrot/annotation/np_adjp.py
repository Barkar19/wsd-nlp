# -*- coding: utf-8 -*-
import sys
import corpus2

class NpAdjpPhrase:
	'''
	Przechowuje informacje o anotowanej frazie (Np lub Agp)
	 - wskaznik do zdania na podstawie ktorego budowana jest fraza
	 - segment rozpinajacy fraze Np lub AdjP (numery tokenow tej frazy)
	 - co jest głową (numer tokenu bedacego glowa)
	 - co jest predykatem (numer tokenu bedacego predykatem)
	 - liste fraz AgP wchodzących w sklad aktualnej frazy (Np lub AdjP)
	'''
	def __init__(self, ann_sent, phrase_bound, tagset, filename, np_adjp_phrase_id, sent_id, phr_str):
		# Zdanie typu corpus2.AnnotatedSentence dla ktorej ustalone zostaly granice frazy NP/AdjP
		self.ann_sent = ann_sent
		# Granice frazy Np/AdjP
		self.phrase_bound = phrase_bound
		# Index wskazujacy na glowe frazy NP/AdjP
		self.ann_head = None
		# lista agpekow wchodzacych w sklad aktualnej frazy NP/AdjP
		self.agp_phr = []
		# Nazwa pliku na podstawie jakiego wygenerowana zostala fraza NP/AdjP
		self.filename = filename
		# Informacja o ciaglosci frazy - ustawiana recznie
		self._is_countinuous = None
		# Identyfikator frazy w pliku - numer frazy w pliku 
		# UWAGA! Numerowanie od 1, nie od 0!!
		self._phrase_identifier = np_adjp_phrase_id
		# identyfiator zdania
		# Np. wczytany bezposrednio z dokumentu korpusu z <sent id="..">
		self._sent_id = sent_id
		# typ frazy => NP/AdjP
		self._phrase_type = phr_str
		
		if tagset:
			# Maska przypadku
			self.cas_mask = tagset.parse_symbol('cas')
			# Maska przyimka
			self.prep_mask = tagset.parse_symbol('prep')
		else:
			self.cas_mask = None
			self.prep_mask = None

		# zapamietuje sobie jeszcze tagset...
		self._tagset = tagset
	
	def agps(self):
		return self.agp_phr

	def head(self):
		return self.ann_head

	def is_countinuous(self):
		return self._is_countinuous

	def phrase_identifier(self):
		return self._phrase_identifier

	def sent_id(self):
		return self._sent_id

	def phrase_type(self):
		return self._phrase_type

	def predicates_type1(self):
		preds = []
		for agp in self.agps():
			preds += agp.first_type_predicates()
		return preds

	def predicates_type2(self):
		preds = []
		for agp in self.agps():
			preds += agp.second_type_predicates()
		return preds

	def segments(self):
		return self.phrase_bound

	def annotated_sentence(self):
		return self.ann_sent

	def agp_heads(self):
		return [agp.head() for agp in self.agps()]
	
	# -----------------------------------------------------------------------------------------

	def get_relative_agp_heads_pos(self):
		'''
		Zwraca relatywne pozycje glow agp/pp wzgledem poczatku NP

		Uwaga! w przypadku wystapienia spojnika itp. spojnik nie jest wliczany w pozycje miedzy agp. tzn:

		2:brak 3:kategorii 4:i 5:podziału 6:wpisów 7:na 8:wstęp 9:i 10:pełen 11:tekst
		0:brak 1:kategorii 2:i 3:podziału 4:wpisów 5:na 6:wstęp 7:i 8:pełen 9:tekst

		AgP/PP Heads    : [2, 3, 5, 6, 8, 11] 
		AgP/PP rel Heads: [0, 1, 2, 3, 5, 7]

		NP Segments: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		AgP Segments: [ [2] ]  [ [3] ]  [ [5] ]  [ [6] ]  [ [7, 8] ]  [ [10, 11] ]
		'''
		agp_head_rel_pos = []
		head_rel_pos = []

		# badamy wzgledem calej np, wiec offset wskazuje przesuniecie wzgledem kolejnych agp
		offset = 0
		for agp in self.agps():
			try:
				if agp is None:
					continue
				else:
					agp_head_rel_pos.append(agp.segments().index(agp.head()) + offset)
					head_rel_pos.append(self.segments().index(agp.head()))
					offset += (len(agp.segments()))
			except Exception, e:
				pass
		return head_rel_pos

	def rel_head(self):
		'''
		Zwraca pozycje glowy NP/AdjP wzgledem poczatku aktualnej frazy
		'''
		for r, h in self.get_rel_map_agp_heads().iteritems():
			if h == self.head():
				return r
		return None

	def get_rel_map_agp_heads(self):
		'''
		Zwraca mape dla pozycji relatywnych wzgledem frazy do pozycji wzgledem zdania
		'''
		hds = self.agp_heads()
		rel = self.get_relative_agp_heads_pos()
		rel_hds_map = dict()
		if len(rel) == len(hds):
			for i, r in enumerate(rel):
				rel_hds_map[r] = hds[i]
		return rel_hds_map
