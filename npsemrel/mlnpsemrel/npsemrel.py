#!/usr/bin/python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

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
The main application to recognize semantic roles into nominal phrases.
Uses saper to recognize some semantic and syntatic informations.
Runs fextor to recognize features and fextor2lexcsd to converts results
to LexCSD Matrix.

Sample usage (learning mode):
  python npsemrel.py \
      --cfg-saper-file cfg/saper_npsemrel.ini \
      --cfg-fextor-file cfg/fextor_npsemrel.ini \
      --cfg-lexcsd-file cfg/lexcsd_npsemrel.ini \
      --temp-dir temp_dir
      --model-dir model_dir
      --index ~/dokumenty/Projekty/CLARIN/Kamienie/M24-A12-2015-05-25-kpwr-np_sem_roles/wikinews.idx.org
      --learn
"""

import os, sys, datetime
from mlnpsemrel import test_learn

import argparse
try:
  import argcomplete
except ImportError:
  argcomplete = None

def make_parser(desc=__doc__):
  """!
  Makes ArgumentParser

  @param desc Application description
  @type desc: String
  """
  aparser =argparse.ArgumentParser(prog="NPSemrel", description=desc)
  # configuration files
  aparser.add_argument('--cfg-saper-file', dest='cfg_saper',
      required=True, help=('Saper configuration file'))
  aparser.add_argument('--cfg-fextor-file', dest='cfg_fextor',
      required=True, help=('Fextor configuration file'))
  aparser.add_argument('--cfg-lexcsd-file', dest='cfg_lexcsd',
      required=True, help=('LexCSD configuration file'))
  # a files to learn or test
  aparser.add_argument('--tagset', dest='tagset', required=False,
      default='nkjp', help=('Tagset used into files.'))
  aparser.add_argument('--index', dest='corp_index', required=False,
      help=('Index to corpora files (ccl and rel-ccl). The files are listed '
        'in separated lines, each line contains path to ccl file and '
        'rel-ccl file with semicolon used as separator'))
  aparser.add_argument('-c', '--ccl-file', dest='ccl_file', required=False,
      help=('Path to ccl file. Where test mode is uses.'))
  aparser.add_argument('-r', '--rel-ccl-file', dest='rel_ccl_file',
      required=False, help=('Path to ccl file. Where test mode is uses.'))
  # temp and model dirs
  aparser.add_argument('--temp-dir', dest='temp_dir', required=False,
      default='temp_dir', help=(
        'Directory where all temporary files will are stored'))
  aparser.add_argument('--model-dir', dest='model_dir', required=False,
      default='model_dir', help=('Directory for classifier model store.'))
  # learning mode enabling
  aparser.add_argument('--learn', dest='learn', required=False,
      action='store_true', default=False,
      help=('Use this option to learn classifier model. If you use this '
        'option then the corpora have to be sapered before.'))
  aparser.add_argument('--cache', dest='cache', required=False,
      action='store_true', help=('If This option is enabled then the '
        'files from the steps are also stored into temporary dir'))

  if argcomplete:
    argcomplete.autocomplete(aparser)
  return aparser

def check_arguments(args):
  """!
  The function checks the correctness of command line arguments

  @param args Arguments from command line
  @type: List of params

  @return List of messages with not correct options
  @rtype List of strings
  """
  msgs = []
  # Check if --index is not enabled and -c and -r is not given
  if not args.corp_index and (not args.ccl_file or not args.rel_ccl_file):
    msgs.append('Parameters -c and -r are required!')
  # If --learning then --index have to be given
  if args.learn and not args.corp_index:
    msgs.append('If learning is enabled, then --index have to be given')
  # if not learning and not corp idx and
  if args.corp_index and (args.ccl_file or args.rel_ccl_file):
    msgs.append('If --index then -c and -r cannot be given.')
  return msgs

def prepare_dirs(model_dir, temp_dir):
  """!
  The function check existing of temporary and model dirs. If not exists
  then creates it.

  @param model_dir Path to directory where model will be stored
  @type model_dir: String

  @param temp_dir Path to temporary directory
  @type temp_dir: String
  """
  if not os.path.exists(model_dir):
    os.makedirs(model_dir)
  if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

def _generate_prefix():
  """!
  The method generates prefix for all files generated in single run.

  Prefix is generated based on the date and time like a:
                15.09.01-17:11:09

  @return generated prefix
  @rtype: String
  """
  TIME_STR_FORMAT="%y.%m.%d-%H:%M:%S"
  curr_date = datetime.datetime.today()
  return curr_date.strftime(TIME_STR_FORMAT)

def main(argv=None):
  p = make_parser()
  args = p.parse_args(argv)

  # check correctness of arguments
  msgs = check_arguments(args)
  if len(msgs):
    for msg in msgs:
      print >> sys.stderr, msg
    return 0

  # prepare temporary and model directories
  prepare_dirs(args.model_dir, args.temp_dir)

  prefix = _generate_prefix()
  # FIXME: Learning mode
  classifier_model = test_learn.learn(
      corp_index_path=args.corp_index,
      tagset=args.tagset,
      temp_dir=args.temp_dir,
      model_dir=args.model_dir,
      saper_config=args.cfg_saper,
      fextor_config=args.cfg_fextor,
      lexcsd_config=args.cfg_lexcsd,
      cache=args.cache,
      prefix=prefix)
  #model = test_learn.learn() if args.learn else \
  #    test_learn.load_model(args.model_dir)

if __name__ == '__main__':
  main()
