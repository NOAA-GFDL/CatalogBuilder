#!/usr/bin/env python

""" 
Tests that a dynamically generated catalog (produced by the GitHub Actions CI workflow) can be
opened by intake-esm and returns a pandas DataFrame. The catalog JSON is downloaded as a
workflow artifact before this test runs. The test is marked xfail because it depends on CI
artifacts that may not be present in all environments.
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
  """Opens the intake-esm datastore at catspec and returns the catalog object. Returns None if the catalog cannot be opened."""
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
  catspec = pathlib.Path(os.path.dirname(__file__)).parent / '../workflow-artifacts1/gfdl_autotest_from_yaml.json'
  cat = load_cat((str(catspec)))
  try:
    assert isinstance(cat.df, pd.DataFrame),"test failed"
  except BaseException as e:
     assert cat!=None,"opening of esm datastore failed"+str(e)
