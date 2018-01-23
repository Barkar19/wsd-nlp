"""!
This module contains helper functions to loading, learning and testing
classifier model
"""

import tempfile
from stdmods import cclutils
from ltlearn.io import arff
from ltcore.io.matrix import load_matrix

def _read_corpora_index_doc(corp_index_path, tagset):                                
  """! 
  Reads corpora index file.                                                      
                                                                                 
  Corpora index file contains list of files belonging to corpora, in each line
  the pair of files is stored: ccl-file and relccl-file separated with
  semicolon.                                                                     
                                                                                 
  @param corp_index_path Path to ndex to corpora files. Contains pairs of files: 
         cclfile and relcclfile separated by semicolon
  @type corp_index_path String
                                                                                 
  @param tagset Tagset used into corpira
  @type tagset: String
                                                                                 
  @return List of read corpus2.Documents
  @rtype Lisf of corpus2.Document
  """                                                                            
  ccl_relccl_files = []                                                          
  with open(corp_index_path, 'rt') as cin:                                    
    for line in cin:                                                             
      ccl_file, rel_ccl_file = line.strip().split(';')                           
      ccl_relccl_files.append(                                                   
          cclutils.read_ccl_and_rel_ccl(ccl_file, rel_ccl_file, tagset))         
  return ccl_relccl_files


def _read_corpora_index_txt(corp_index_path, tagset):
  """!
  Reads corpora index file. 

  Corpora index file contains list of files belonging to corpora, in each line
  the pair of files is stored: ccl-file and relccl-file separated with
  semicolon. That list is returned to user.

  @param corp_index_path Path to ndex to corpora files. Contains pairs of files:
         cclfile and relcclfile separated by semicolon
  @type corp_index_path String

  @param tagset Tagset used into corpira
  @type tagset: String

  @return List of string
  @rtype Lisf of corpus2.Document
  """
  ccl_relccl_files = []
  with open(corp_index_path, 'rt') as cin:
    for line in cin:
      ccl_relccl_files.extend(line.strip().split(';'))
  return ccl_relccl_files

def _read_corpora_index_fextor(corp_index_path, tagset):
  """!
  Reads corpora index file for fextor in -b mode. 

  Corpora index file contains list of files belonging to corpora, in each line
  the pair of files is stored: ccl-file and relccl-file separated with
  semicolon. The list where into number%2==0 are ccl files and number%2==1 are
  relcclfiles (split into Fextor have to be enabled!) is returned to user

  @param corp_index_path Path to ndex to corpora files. Contains pairs of files:
         cclfile and relcclfile separated by semicolon
  @type corp_index_path String

  @param tagset Tagset used into corpira
  @type tagset: String

  @return List of strings
  @rtype Lisf of Strings
  """
  ccl_relccl_files = []
  with open(corp_index_path, 'rt') as cin:
    for line in cin:
      ccl_relccl_files.extend(line.strip().split(';'))
  return ccl_relccl_files

def _save_arff(sparse_matrix, temp_dir, prefix):
  """!
  Save LexCSD matrix to output file.

  @param sparse_matrix the features sparse matrix to be saved.
  @type sparse_matrix: ltcore.matrix.SparseMatrix

  @param tmp_dir Temporary directory
  @type tmp_dir: String

  @param prefix Prefix which will be added to all files generatged in this step
  @type prefix: String

  @return path to created file
  @rtype: String
  """ 
  arff_file = tempfile.NamedTemporaryFile(
      mode='w+t',
      dir=temp_dir,
      prefix='{:}_weka_'.format(prefix),
      suffix='.arff',
      delete=False)
 
  if sparse_matrix.data.shape[0]:
    arff.sparse_matrix_to_arff(arff_file.name, sparse_matrix) 
    return arff_file.name
  return None
