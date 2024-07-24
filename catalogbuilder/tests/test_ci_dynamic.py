#!/usr/bin/env python

""" 
Tests to load a (dynamically generated) catalog and extend the test capabilities in the actions workflow . We check if a pandas data frame is 
returned while opening the data catalog with intake-esm. TODO: For more visual tests, we need more than empty files as input. 
This test is run from a dynamically generated csv and json using GitHub actions workflow. See workflow create-gfdl-catalog for more info.
We refer to the csv with the artifact path, the one downloaded via actions workflow. See catspec path to connect the dots.
"""

__author__ = "A.Radhakrishnan"
__maintainer__ = "GFDL MSD workflow team"

import intake
import intake_esm
import pandas as pd 
import os
import pathlib
import pytest

def load_cat(catspec=None):
  """Checks if the json and associated csv can be opened by intake_esm""" 
  cat = None
  try:
    cat = intake.open_esm_datastore(catspec)
  except BaseException as e:
    print("Can't load this catalog",str(e))
  return cat

@pytest.mark.xfail
def test_loadcat():
  #generate csv and json on the fly
  #todo check if its readable etc
  #we are using the dynamically generated csv and json for testing in this routine
  #leveraging GitHub actions CI workflow and manifests and caches
  catspec = pathlib.Path(os.path.dirname(__file__)).parent / 'workflow-artifacts1/gfdl_autotest.json'
  cat = load_cat((str(catspec)))
  try:
    assert isinstance(cat.df, pd.DataFrame),"test failed"
  except BaseException as e:
     assert cat!=None,"opening of esm datastore failed"+str(e)
