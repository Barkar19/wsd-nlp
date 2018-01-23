import sys

class PhraseDumper:
	'''
	Dokonuje dampu frazy
	'''

	def __init__(self, npadjpman, fstman, sndman):
		self.npadjpman = npadjpman
		self.fstman = fstman
		self.sndman = sndman

	def dump_phrase(self, tagset, dump_mode = 0, out = sys.stdout):
		offset = 0
		min_seg = min(self.npadjpman.np_adjp().segments())

		print >> out, ''
		print >> out, 100 * '-'

		print >> out, self.npadjpman.np_adjp().filename
		print >> out, 'Fraza ciagla:', ('Tak' if self.npadjpman.np_adjp()._is_countinuous == True else 'Nie')
		print >> out, 'Typ frazy:', self.npadjpman.np_adjp().phrase_type()
		if dump_mode == 2:
			print >> out, 'Numer frazy w pliku:', self.npadjpman.np_adjp().phrase_identifier()
	
		# fraza
		print >> out, ' '.join(
				(self.npadjpman.np_adjp().annotated_sentence().tokens()[s].orth_utf8()) \
						for s in self.npadjpman.np_adjp().segments())
	
		if dump_mode == 2:
			# fraza z pozycja w zdaniu
			print >> out, ' '.join(
					(str(i + min_seg) + ':' + 
						self.npadjpman.np_adjp().annotated_sentence().tokens()[s].orth_utf8()) \
								for i, s in enumerate(self.npadjpman.np_adjp().segments()))

		if dump_mode == 1 or dump_mode == 2:
			# fraza z pozycja od 0
			print >> out, ' '.join(
					(str(i) + ':' + 
						self.npadjpman.np_adjp().annotated_sentence().tokens()[s].orth_utf8()) \
								for i, s in enumerate(self.npadjpman.np_adjp().segments()))
		
			# fraza z disambami
			for s in self.npadjpman.np_adjp().segments():
				token = self.npadjpman.np_adjp().annotated_sentence().tokens()[s]
				lexeme = token.get_preferred_lexeme(tagset)
				tag = lexeme.tag()
				print >> out, token.orth_utf8() + '[' + tagset.tag_to_string(tag), '] ',
			print >> out, ''

		if dump_mode == 2:
			print >> out, 'NP/AdjP:['
			# for agp in self.agps():
			for agp in self.npadjpman.sort_agps():
				if agp.is_pp():
					print >> out, '\tPP:[',
				else:
					print >> out, '\tAgP:[',
				
				for i, s in enumerate(agp.segments()):
					if self.fstman.is_pred_type1_at_pos(i + offset):
						print >> out, 'P1(',
					elif self.sndman.is_pred_type2_at_pos(i + offset):
						print >> out, 'P2(',

					if s == self.npadjpman.np_adjp().head():
						print >> out, 'NP/AdjP_H:{' + \
								self.npadjpman.np_adjp().annotated_sentence().tokens()[s].orth_utf8() + \
								'}' + '[' + str(s) + ']' , 
					elif s == agp.head():
						print >> out, 'H:{' + \
								self.npadjpman.np_adjp().annotated_sentence().tokens()[s].orth_utf8() + \
								'}' + '[' + str(s) + ']' ,
					else:
						print >> out, '{' + \
								self.npadjpman.np_adjp().annotated_sentence().tokens()[s].orth_utf8() + \
								'}' + '[' + str(s) + ']' ,

					if self.fstman.is_pred_type1_at_pos(i + offset) or self.sndman.is_pred_type2_at_pos(i + offset):
						print >> out, ')',

				print >> out, ']'
				offset += len(agp.segments())
			print >> out, ']'
			print >> out, 'NP/AdjP Head    :', self.npadjpman.np_adjp().head()
			print >> out, 'NP/AdjP rel Head:', self.npadjpman.np_adjp().rel_head()
			print >> out, 'AgP/PP Heads    :', self.npadjpman.np_adjp().agp_heads()
			print >> out, 'AgP/PP rel Heads:', self.npadjpman.np_adjp().get_relative_agp_heads_pos()
			print >> out, 'NP Segments: ', self.npadjpman.np_adjp().segments()
			print >> out, 'AgP/PP Segments: [',
			for agp in self.npadjpman.np_adjp().agps():
				print >> out, agp.segments(),
			print >> out, ']'
