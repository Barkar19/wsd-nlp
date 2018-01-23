import sys
import tempfile
from argparse import Namespace                                                   

from mlnpsemrel import ml_io

from fextor import Fextor
from fextor.apps import fextor2lexcsd 

from ltcore.io import matrix 

def run_fextor_batch(fextor_config_path, corp_index_path, 
    tmp_dir, prefix, tagset):
  """
  Runs fextor for given corpus index file. 

  Store extracted features into file and returns path to this file.

  @param fextor_config_path Path to fextor config
  @type fextor_config_path: String

  @param corp_index_path Path to corpus index. One pair of ccl/relccl file is
         stored into the file in one line, ccl file is separated with semicolon 
         from rel ccl file
  @type corp_index_path: String
  
  @param tmp_dir Temporary directory
  @type tmp_dir: String

  @param prefix Prefix which will be added to all files generatged in this step
  @type prefix: String

  @param tagset Tagsed used into corpora
  @type tagset: String

  @return Path to csv-file created by Fextor or None if any exception was thrown
          by Fextor application
  @rtype: String or None
  """
  files = ml_io._read_corpora_index_fextor(corp_index_path, tagset)
  fex_file = tempfile.NamedTemporaryFile(
      mode='w+t',
      dir=tmp_dir,
      prefix='{:}_fextor_'.format(prefix),
      suffix='.csv',
      delete=False)

  fex = Fextor(
    ini_file_path=fextor_config_path,
    input_files=files,
    batch_mode=False,
    tagset_name=tagset,
    output_file_path=fex_file.name,
    split_relations_mode=True,
    input_format='document',
    reader=None)

  try:
    fex.run()
    return fex_file.name
  except Exception:
    raise

def run_fex2lex(fextor_config_path, csv_fextor_output, 
    tmp_dir=None, prefix='', cache=False):
  """!
  Runs fextor2lexcsd, converts fextor output to LexCSD matrix.

  Makes matrix in LexCSD (wrapper) format and returns it.
  If temp_dir is given, then matrix is also stored into them.
  If cache is enabled then arf will be generated.

  @param fextor_config_path Path to fextor config
  @type fextor_config_path: String

  @param csv_fextor_output Path to CSV file with fexotr output
  @type: String

  @param tmp_dir Temporary directory, as default is set to None
  @type tmp_dir: String

  @param prefix Prefix which will be added to all files generatged in this step
  @type prefix: String

  @param cache Boolean option to store cache files such as arffs.
  @type cache: Boolean

  @return A tuple of LexCSD matrix and path to stored matrix (or None in case
          when tmp_dir is not to set)
  @rtype: Tuple of (LexCSD Matrix, String) or (LexCSD Matrix, None)
  """
  f2l_file = tempfile.NamedTemporaryFile(
       dir=tmp_dir,
       prefix='{:}_fex2flex_'.format(prefix),
       suffix='.bz2',
       delete=False)

  args = _make_f2l_args(
      fextor_config_path=fextor_config_path,
      fextor_out_csv=csv_fextor_output,
      output_matrix_file_path=f2l_file.name)

  args.out_matrix = f2l_file.name
  lmatrix = fextor2lexcsd.make_matrix(args)
  fextor2lexcsd.make_tarfile(args, lmatrix)
  smatrix = matrix.load_matrix(f2l_file.name)

  if cache:
    arff_file = ml_io._save_arff(smatrix, tmp_dir, prefix)

  return (smatrix, None if not tmp_dir else f2l_file.name)

def make_selection(lexcsd_config, matrix_to_select, temp_dir):
  return matrix_to_select

def _make_f2l_args(fextor_config_path, fextor_out_csv, output_matrix_file_path):
  """!
  Makes arguments for fextor2lexcssd allication

  @param fextor_config_path
  @type: fextor_config_path

  @param fextor_out_csv
  @type: fextor_out_csv

  @param output_matrix_file_path
  @type: output_matrix_file_path

  @return Namespace of arguments for fextor2lexcsd
  @rtype argparser.Namespace
  """
  args = Namespace()
  args.ini_config_file = fextor_config_path
  args.input_csv = fextor_out_csv
  args.out_matrix = None
  args.class_labels = True
  args.contexts = False
  args.groups_id = False
  args.info = 'NPSemrel'
  args.verbose = False
  args.model = None
  return args
