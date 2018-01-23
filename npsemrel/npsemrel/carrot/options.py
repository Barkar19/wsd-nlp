class Options:
	def __init__(self, filename):
		self.filename = filename

		# slownik postaci:
		# 	nazwa zbioru: licznosc 
		# 	np.
		# ustawy:16
		# licznosci plikow
		self.np_files = dict()
		self.adjp_files = dict()
		# licznosci fraz
		self.np_phrases = dict()
		self.adjp_phrases = dict()
			
		self.np_min_agp_count = None
		self.adjp_min_agp_count = None
		
		# -> powiazanie numeru reguly z operatorem
		self.operators = dict()
		self.rules = dict()
	
	def parse_cfg(self):
		from ConfigParser import RawConfigParser
		config = RawConfigParser()
		with open(self.filename, 'r') as ini_file:
			config.readfp(ini_file)
			for k, v in config.items('np_files'):
				self.np_files[k] = int(v)
			for k, v in config.items('adjp_files'):
				self.adjp_files[k] = int(v)
			
			for k, v in config.items('np_phrases'):
				self.np_phrases[k] = int(v)
			for k, v in config.items('adjp_phrases'):
				self.adjp_phrases[k] = int(v)

			self.np_min_agp_count = config.getint('main', 'np_min_agp_count')
			self.adjp_min_agp_count = config.getint('main', 'adjp_min_agp_count')
