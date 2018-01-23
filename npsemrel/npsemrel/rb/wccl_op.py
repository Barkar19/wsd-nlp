# -*- coding: utf-8 -*-

import sys
import os
import codecs
import wccl

from npsemrel.carrot import annotation 

class WcclOp:
	'''
	Czytnik operatorow wccl oraz narzedzie do ich wykonywania
	'''
	def __init__(self):
		# self.ops = dict()
		self.ops = []
	
	def get_ops(self):
		return self.ops

	def run_wccl_operator(self, ts, ann_sent):
		'''
		Uruchamia wszystkie operatory WCCL na przekazanym zdaniu
		'''
		if ann_sent == None:
			return
		asent = ann_sent
		for (sem_name, op) in self.ops:
			con = wccl.SentenceContext(asent.clone_shared())
			con.goto_start()
			res = op.base_apply(con).to_string(ts)
			if res == 'True':
				return sem_name
		return None
	
	def load_wccl_operators(self, file_path, tagset):
		'''
		Laduje operatory zapisane w pliku
		'''
		print >> sys.stderr, "Loading operators from:", file_path
		p = wccl.Parser(tagset)
		f = p.parseWcclFileFromPath(file_path)
		self.ops.extend(f.gen_all_op_pairs())
