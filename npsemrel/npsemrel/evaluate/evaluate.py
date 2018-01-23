import os
import pickle
import datetime
import corpus2

import npsemrel.carrot.annotation as annotation
import defender.syn_rel as syntax_relation

class SingleResult:
	'''
	Klasa opisuje pojedyncza decyzje lingwisty dla pary/trojki
	'''
	def __init__(self, syntax_relation):
		# Wykryta relacja skladniowa
		self.syntax_relation = syntax_relation
		# Czy poprawna jest para/trojka? -> relacja skladniowa
		self.correct_pair_triple = False
		# czy wykryta relacja semantyczna jest niepoprawna?
		self.incorrect_auto_relation = False
		# nazwa recznie przypisanej relacji semantycznej
		self.manual_semantic_relation = ''
		# nazwa Wykrytej relacji semantycznej
		self.auto_semantic_relation = None

class OutputDirs:
	'''
	Klasa opisujaca wyjsciowe katalogi
	'''
	def __init__(self, out_directory, phr_str):
		if out_directory and phr_str:
			self.output_directory = os.path.join(out_directory, phr_str)
			if not os.path.exists(self.output_directory):
				os.makedirs(self.output_directory)

		self.files_pref = {
			1:'p_skl-np_sem_-r_sem',	# jezeli poprawna jest para/trojka oraz niepoprawna jest wykryta relacja semantyczna
			2:'p_skl-p_sem',					# jezeli poprawna jest para/trojka oraz poprawna jest wykryta relacja semantyczna
			3:'p_skl-nwyk_sem-r_sem',	# jezeli poprawna jest para/trojka oraz nie zostala wykryta relacja semantyczna a jest
			4:'p_skl-bez_sem',				# jezeli poprawna jest para/trojka oraz nie ma relacji semantycznej
			5:'np_skl-np_sem',				# wykryta relacja semantyczna jest niepoprawna, poniewaz wykryta relacja skladniowa jest niepoprawna 
			6:'nwyk_skl-r_skl_r_sem',	# jezeli nieywkryta jest para/trojka/relacja semantyczna a jest
			7:'np_skl-bez_sem'				# jezeli niepoprawna jest para/trojka to wiadomo, ze nie jest poprawna rowniez relacja semantyczna
		}
	
	def make_result_filename_based_on_single_result(self, single_result):
		# ustalam prefix pliku w zaleznosci od typu odpowiedzi uzytkownika, 
		# pobieram prefix z evaluate.output_dirs.files_pref
		file_prefix = ''
		if single_result.correct_pair_triple == True:
			if single_result.incorrect_auto_relation == True:
				# jezeli poprawna jest para/trojka oraz niepoprawna jest wykryta relacja semantyczna: 
				file_prefix = self.files_pref[1]
			else:
				if single_result.auto_semantic_relation != None:
					# jezeli poprawna jest para/trojka oraz poprawna jest wykryta relacja semantyczna:
					file_prefix = self.files_pref[2]
				else:
					if single_result.manual_semantic_relation != None:
						# jezeli poprawna jest para/trojka oraz nie zostala wykryta relacja semantyczna a jest:
						file_prefix = self.files_pref[3]
					else:
						# jezeli poprawna jest para/trojka oraz nie ma relacji semantycznej:
						file_prefix = self.files_pref[4]
		else:
			if single_result.incorrect_auto_relation == True:
				# wykryta relacja semantyczna jest niepoprawna, poniewaz wykryta relacja skladniowa jest niepoprawna
				file_prefix = self.files_pref[5]
			else:
				if single_result.manual_semantic_relation != None and single_result.manual_semantic_relation != False:
					# jezeli nieywkryta jest para/trojka/relacja semantyczna:
					file_prefix = self.files_pref[6]
				else:
					# jezeli niepoprawna jest para/trojka to wiadomo, ze nie jest poprawna rowniez relacja semantyczna:
					file_prefix = self.files_pref[7]
		# nazwa pliku bez rzszerzenia...
		fname = os.path.basename(single_result.syntax_relation.np_adjp_phrase().filename).replace('.', '_')

		# czas podjecia decyzji
		now = datetime.datetime.now()
		file_prefix += '_' + str(single_result.syntax_relation.np_adjp_phrase().phrase_identifier())
		timestamp_str = now.strftime("%Y-%m-%d_%H:%M:%S")
		# nazwa pliku
		out_filename = '%s_%s_%s.bin' % (file_prefix, fname, timestamp_str)
		# sciezka do pliku
		out_file_path = os.path.join(self.output_directory, out_filename)
		return out_file_path

	def save_single_result(self, out_file_path, user_decision):
		'''
		Funkcja usuwa wszystkie obiekty, ktore nie moga zostac zserializowane przez pickla
		Wszystkie utworzone obiekty Swiga (z corpus2) dlatego w celu zapewnienia poprawnego
		dzialania zapisanych obiektow po ich wczytaniu, nalyz uzyc metody load_single_result

		Jezeli istnieje juz plik o zadanej nazwie, wtedy automatycznie dodawany jest kolejny 
		numer porzadkowy do nazwy pliku. np aaaaaa.bin => aaaaaa-1.bin, aaaaaa-2.bin itd.
		Przydaje sie to wmomencie kiedy uzytkownik podaje recznie relacje skladniowe/semantyczne
		po czym nastepuje ich zapis w plikach, wtedy w jednej sekundzie moze zapisac sie wiele
		plikow, dlatego potrzeba jest rozroznic ich nazwy
		'''
		# np/adjp
		np_adjp = annotation.np_adjp.NpAdjpPhrase(
				None, # annotated sentence
				user_decision.syntax_relation.np_adjp_phrase().phrase_bound,
				None, # tagset
				user_decision.syntax_relation.np_adjp_phrase().filename,
				user_decision.syntax_relation.np_adjp_phrase().phrase_identifier(),
				user_decision.syntax_relation.np_adjp_phrase().sent_id(),
				user_decision.syntax_relation.np_adjp_phrase().phrase_type()
		)
		np_adjp._is_countinuous = user_decision.syntax_relation.np_adjp_phrase().is_countinuous()
		np_adjp.ann_head = user_decision.syntax_relation.np_adjp_phrase().head()
		for magp in user_decision.syntax_relation.np_adjp_phrase().agps():
			agp = annotation.agp.agpphrase()
			agp.agp_head_idx = magp.agp_head_idx
			agp.agp_pred_idx_t1 = magp.agp_pred_idx_t1
			agp.agp_pred_idx_t2 = magp.agp_pred_idx_t2
			agp.seg = magp.seg
			agp._prep_lexeme = None
			np_adjp.agp_phr.append(agp)

		# syntax relation
		syntax_rel = syntax_relation.SyntaxRelation(
				np_adjp, 
				user_decision.syntax_relation.tokens_positions()
		)
		syntax_rel.ann_sentence = None 

		# single result -> based on user_decision
		s_res_pickled = SingleResult(syntax_rel)
		s_res_pickled.correct_pair_triple = user_decision.correct_pair_triple
		s_res_pickled.incorrect_auto_relation = user_decision.incorrect_auto_relation
		s_res_pickled.manual_semantic_relation = user_decision.manual_semantic_relation
		s_res_pickled.auto_semantic_relation = user_decision.auto_semantic_relation

		if os.path.exists(out_file_path):
			append_number = 1
			m_out_file_path = None
			f_path = out_file_path.replace('.bin', '')
			ext = 'bin'
			while True:
				m_out_file_path = "%s-%d.%s" % (f_path, append_number, ext)
				if os.path.exists(m_out_file_path):
					append_number += 1
				else:
					break
			# pickle single_result
			with open(m_out_file_path, 'wb') as fout:
				pickle.dump(s_res_pickled, fout, pickle.HIGHEST_PROTOCOL)
		else:
			# pickle single_result
			with open(out_file_path, 'wb') as fout:
				pickle.dump(s_res_pickled, fout, pickle.HIGHEST_PROTOCOL)

	def load_single_result(self, in_file_path, tagset):
		'''
		Wczytuje zapisanego pickla - zapewnie poprawnosc wzgledem calej struktury danych
		klasy corpus2 nie moga byc picklowane, zatem wczytuje info z pickla o pliku na podstawie
		ktorego zbudowac klasy corpus2 aby byly zgodnie z tymi przed picklowaniem ->
			filename, _phrase_identifier oraz sent_id
		'''
		s_result = None
		with open(in_file_path, 'rb') as fin:
			s_result = pickle.load(fin)
		
		# annotated sentence for np/adjp phrase
		s_result.syntax_relation._np_adjp_phrase.ann_sent = self.load_annotated_sentence(
				tagset,
				s_result.syntax_relation.np_adjp_phrase().filename,
				s_result.syntax_relation.np_adjp_phrase()._phrase_identifier,
				s_result.syntax_relation.np_adjp_phrase().sent_id())
		s_result.syntax_relation._np_adjp_phrase.cas_mask = tagset.parse_symbol('cas')
		s_result.syntax_relation._np_adjp_phrase.prep_mask = tagset.parse_symbol('prep')
		
		# syntax relation -> annotated sentence
		s_result.syntax_relation.ann_sentence = corpus2.AnnotatedSentence()
		for tok_idx_in_np in s_result.syntax_relation.tokens_positions():
			# it's magic! but still working... ;-)
			tok = s_result.syntax_relation.np_adjp_phrase().annotated_sentence().tokens()[
					s_result.syntax_relation.np_adjp_phrase().phrase_bound[tok_idx_in_np]]
			s_result.syntax_relation.annotated_sentence().append(tok.clone())

		return s_result

	def load_annotated_sentence(self, tagset, corp_file, phr_id, sent_id):
		'''
		Z zadanego pliku laduje zdanie z okreslonej frazy (phr_id) o zadanym identyfikatorze
		'''
		doc_read = corpus2.CclRelReader(tagset, corp_file, corp_file)
		doc_read.set_option("disamb_only");
		document = doc_read.read()
		for chunk in document.paragraphs():
			np_adjp_num = 0
			for sent in chunk.sentences():
				np_adjp_num += 1
				if sent_id == sent.id() and phr_id == np_adjp_num:
					an_sent = corpus2.AnnotatedSentence().wrap_sentence(sent)
					return an_sent
		return None

	def load_evaluated_phrases(self, tagset):
		'''
		Laduje pojedyncze decyzje uzytkownika z zadanego katalogu wyjsciowego (obiekt out_dirs)
		Zwraca liste single_results
		'''
		single_results = []
		for eval_file in os.listdir(self.output_directory):
			eval_file = os.path.join(self.output_directory, eval_file)
			sres = self.load_single_result(eval_file, tagset)
			single_results.append(sres)
		return single_results

rel_available_dict = {
		0:'NIEPOPRAWNA RELACJA SKLADNIOWA',
		1:'OBIEKT', 
		2:'SUBIEKT', 
		3:'AGENS',
		4:'SUBIEKT NIEAGENTYWNY',
		5:'PRZYCZYNA',
		6:'WLASCIWOSC', 
		7:'KOLEJNOSC', 
		8:'ILOSC', 
		9:'MIEJSCE', 
		10:'CZAS', 
		11:'POSIADACZ', 
		12:'EKSPERIENCER', 
		13:'INSTRUMENT', 
		14:'REZULTAT', 
		15:'MATERIAL', 
		16:'PRZEZNACZENIE', 
		17:'RODZINA', 
		18:'MERONIMIA MIEJSCA', 
		19:'MERONIMIA CZASU', 
		20:'INNA RELACJA SEMANTYCZNA'
}
