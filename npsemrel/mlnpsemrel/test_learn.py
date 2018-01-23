"""!
This module contains helper functions to loading, learning and testing
classifier model
"""

import os
from ltcore.utils.config import load_config

from mlnpsemrel import fextract                                         
from mlnpsemrel.constants import CLASSIFIER_MODEL_NAME

import ltlearn.classification.makers.maker as ltlearnmkr

def learn(corp_index_path, tagset, temp_dir, model_dir, 
    saper_config, fextor_config, lexcsd_config, cache,
    prefix):
  """!
  The learning mode of npsemrel.

  For features extraction Fextor is used, features are converted with
  Fextor2LexCSD and LexCSD is used to selection, transformation and learning
  process. All results from single steps are stored into temporary dir, the
  output model is stored into model directory. 

  @param corp_index_path Path to ndex to corpora files. Contains pairs of files:
         cclfile and relcclfile separated by semicolon
  @type corp_index_path String

  @param tagset Tagset used into corpora
  @type tagset: String

  @param temp_dir Dictionary where all single results from steps will are stored
  @type temp_dir: String

  @param model_dir Dictionary where output model named as
          mlnpsemrel.constants.CLASSIFIER_MODEL_NAME will be stored
  @type model_dir: String

  @param saper_config Path to Saper config
  @type saper_config: String

  @param saper_config Path to Saper config
  @type fextor_config: String

  @param lexcsd_config Path to Saper config
  @type lexcsd_config: String

  @param cache Boolean attribute to use or dont generates cache files
  @type cache: Boolean

  @param prefix Prefix which will be added to all files generatged in this step
  @type prefix: String

  @return Learn model of classifier
  """

  # run fextor
  fextor_csv_out = fextract.run_fextor_batch(
      fextor_config_path=fextor_config,
      corp_index_path=corp_index_path,
      tmp_dir=temp_dir,
      prefix=prefix,
      tagset=tagset)
  
  # convert fextor output to lexcsd matrix
  if not fextor_csv_out:
    return
  (matrix, matrix_path) = fextract.run_fex2lex(
      fextor_config_path=fextor_config,
      csv_fextor_output=fextor_csv_out,
      tmp_dir=temp_dir,
      prefix=prefix,
      cache=cache)

  # Runs selection
  matrix = fextract.make_selection(
      lexcsd_config=lexcsd_config,
      matrix_to_select=matrix,
      temp_dir=temp_dir)

  # classification
  maker = ltlearnmkr.Maker()
  classifiers = maker.make_classifiers_from_config(lexcsd_config)
  assert len(classifiers) == 1, "Only one classifier should be set into config"
  cl = classifiers[0]
  cl.learn(matrix)

  model_file = os.path.join(model_dir, CLASSIFIER_MODEL_NAME)
  cl.serialize(model_file)

def load_model(model_dir, model_name=CLASSIFIER_MODEL_NAME):
  """!
  Loads model from given directory. 

  Name of the model is always the same, and named as npsemrel_model.bz2

  @desc model_dir Directory where the classifier model was stored.
  @type model_dir: String
  """
  print 'load model {} {}'.format(model_dir, model_name) #, model_name)
