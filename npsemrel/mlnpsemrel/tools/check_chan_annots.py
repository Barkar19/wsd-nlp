#!/usr/bin/python
# -*- coding: utf-8 -*-
#PYTHON_ARGCOMPLETE_OK 

# <one line to give the library's name and an idea of what it does.>
# Copyright (C) 2014  <copyright holder> <email>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

"""
Sprawdza czy w zadanym korpusie dla każdej relacji semantycznej znajduje się
anotacja defendera (automatycznie dodana) oraz jakakolwiek anotacja
maltowa (również dodana automatycznie). Zwraca wynik jaki procent relacji
defenderowych pokryty jest rolami semantycznymi oraz jaki procent relacji
maltowych pokryty jest rolami semantycznymi.
"""

import io
import corpus2
from stdmods import cclutils

import argparse
try:
  import argcomplete
except ImportError:
  argcomplete = None


def make_parser(descr=__doc__):
  """!
  Makes argument parser

  @param descr Application description
  @type descr: Str

  @return Built parser
  @rtype: argparse.ArgumentParser
  """
  aparser = argparse.ArgumentParser(description=descr)
  aparser.add_argument('-i', '--index', dest='index',
      required=True, help=('Index of corpora files'))

  return aparser

def check_document(doc):
  """!
  """
  MANUAL_SEMRELS_CHANNELS = [
      "argument",
      "predykat",
      "argument_adjp",
      "predykat_adjp"]

  MALT_CHANNEL = "malt"
  DEFENDER_CHANNEL = "deepened_chunker"

  rels = doc.relations()
  for p in doc.paragraphs():
    for s in p.sentences():
      asent = corpus2.AnnotatedSentence.wrap_sentence(s)
      achans = asent.all_channels()

      for ch in achans:
        if ch in MANUAL_SEMRELS_CHANNELS:
          malt_chan = def_chan = None
          man_chan = asent.get_channel(ch)
          if MALT_CHANNEL in achans:
            malt_chan = asent.get_channel(MALT_CHANNEL)
          if DEFENDER_CHANNEL in achans:
            def_chan = asent.get_channel(DEFENDER_CHANNEL)

          if not malt_chan and not def_chan:
            print ':('

          man_segs = man_chan.segments()
          def_segs = def_chan.segments()
          malt_segs = malt_chan.segments()

          for idx, annum in enumerate(man_segs):
            if annum:
              if def_segs[idx]:
                print 'man+def'
              else:
                print doc.path()
                print 'brak man+def'
              
              if malt_segs[idx]:
                print 'malt+def'
              else:
                print doc.path()
                print 'brak malt+def'
          #print '-'.join(str(s) for s in man_segs)
          #print '-'.join(str(s) for s in def_segs)
          #print '-'.join(str(s) for s in malt_segs)
          print 50 * '-'

def main(argv=None):
  parser = make_parser()
  args = parser.parse_args(argv)

  # read index
  with io.open(args.index) as iin:
    for rcl in iin:
      ccl, relccl = rcl.strip().split(';')
      check_document(cclutils.read_ccl_and_rel_ccl(ccl, relccl))

if __name__ == '__main__':
  main()
