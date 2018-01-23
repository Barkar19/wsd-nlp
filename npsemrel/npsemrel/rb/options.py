class Options:
	def __init__(self, filename):
		self.filename = filename
		self.operators = dict()
		self.rules = dict()
	
	def parse_wccl_cfg(self):
		from ConfigParser import RawConfigParser
		config = RawConfigParser()
		with open(self.filename, 'r') as ini_file:
			config.readfp(ini_file)
			for k, v in config.items('operators'): 
				self.operators[k] = v
			for k, v in config.items('rules'): 
				self.rules[k] = v
			
			self.left_side_ops = [opname.strip().lower() for opname in config.get('direction', 'left_side_operators').split(',')]
			self.right_side_ops = [opname.strip().lower() for opname in config.get('direction', 'right_side_operators').split(',')]
