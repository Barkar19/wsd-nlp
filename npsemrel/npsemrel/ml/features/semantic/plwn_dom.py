from npsemrel.carrot.db import db
import npsemrel.ml.features.semantic.plwn_base23elems as plwni

class PlwndomFeature(plwni.Plwnbase23ElemsFeature):
	'''
	Ekstraktor cechy: dziedzina tokenu (dziedzina pobierana jest ze slowosieci
	z przekazanego polaczenia do bazy). Wykorzystuje anotacje (wartosc dla atrybutu) 
	dla tokenu (atrybut o nazwie sense:ukb:syns_id)
	'''

	def __init__(self, db_config_file):
		super(PlwndomFeature, self).__init__(
				self.__get_plwndom_for_token,
				"_plwndom")

		self.dbconnection = db.DB().connect(db_config_file)
		if not self.dbconnection:
			print >> sys.stderr, 'Cannot connect to DB (%)!' % db_config_file
			exit(1)

	def __get_plwndom_for_token(self, syn_id):
		'''
		Dla zadanego synsetu, odczytuje z bazy jego dziedzine

		syn_id - identyikator synsetu
		'''
		if syn_id == None or self.dbconnection == None:
			return None
		return self.__get_domid_from_plwordnet(syn_id)

	def __get_domid_from_plwordnet(self, synid):
		query = 'SELECT domain FROM lexicalunit LU JOIN unitandsynset UAS ON ' \
				' (LU.ID = UAS.LEX_ID) WHERE UAS.SYN_ID = %s LIMIT 1;' % (synid)
		cursor = self.dbconnection.cursor()
		cursor.execute(query)
		syn_domid = cursor.fetchone()
		if syn_domid:
			return syn_domid[0]
		return None
