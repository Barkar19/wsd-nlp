# -*- coding: utf-8 -*-

import unittest
from wosedon.lesk_filters import POS
from wosedon.utils.leskfilteroptions import LeskFilterOptions

import corpus2
from wosedon.context.document import Document




def leniter(i):
  """ Lenght of any iterable """
  return sum(1 for e in i)


class TestLeskFilterPOS(unittest.TestCase):

  def setUp(self):
    self.tagset = corpus2.get_named_tagset('nkjp')
    
    cclreader = corpus2.CclRelReader(self.tagset, 'tests/#Data/wiki_ccl.xml', 'tests/#Data/wiki_ccl.xml')
    ccldoc = cclreader.read()
    self.document = Document(self.tagset, ccldoc, ccldoc.relations())


  def test_it(self):
    opts = LeskFilterOptions()
    opts.set_input_file('tests/#Data/leskfilters/pos')
    self.filter = POS(self.tagset, opts)
    
    doc = self.document.next()
    while doc:
      for t in doc.tokens():
        lexeme = t.get_preferred_lexeme(self.tagset)
        pos = self.tagset.get_pos_name(lexeme.tag().get_pos_index())
        if pos in ['adv', 'inf', 'ign']:
          self.assertNotIn(lexeme, self.filter)
        else:
          self.assertIn(lexeme, self.filter)
          
      doc = self.document.next()


  def test_reversed(self):
    opts = LeskFilterOptions()
    opts.set_input_file('tests/#Data/leskfilters/pos')
    opts.set_allow_only(True)
    self.filter = POS(self.tagset, opts)
    
    doc = self.document.next()
    while doc:
      for t in doc.tokens():
        lexeme = t.get_preferred_lexeme(self.tagset)
        pos = self.tagset.get_pos_name(lexeme.tag().get_pos_index())
        if pos not in ['adv', 'inf', 'ign']:
          self.assertNotIn(lexeme, self.filter)
        else:
          self.assertIn(lexeme, self.filter)
          
      doc = self.document.next()


