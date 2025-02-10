import os,sys

def test_import1():
  import catalogbuilder
  assert catalogbuilder is not None
  
def test_import2():
  import catalogbuilder.intakebuilder
  assert catalogbuilder.intakebuilder is not None
  
def test_import3():
  from catalogbuilder.intakebuilder import gfdlcrawler, CSVwriter, configparser
  assert not None in [gfdlcrawler, CSVwriter, configparser]


