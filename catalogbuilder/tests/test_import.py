import os,sys

#def check_import():
#  try:
#    import catalogbuilder
#    import catalogbuilder.intakebuilder
#    from catalogbuilder.intakebuilder import gfdlcrawler, CSVwriter, configparser
#  except ImportError:
#    print("The module intakebuilder is not installed. Do you have intakebuilder in your sys.path or have you activated the conda environment with the intakebuilder package in it? ")
#    print("Attempting again with adjusted sys.path ")
#
#    try:
#      #candobetter with actual conda package built before this, but this is a decent test for those that do not use conda package
#      sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/catalogbuilder")
#      from intakebuilder import gfdlcrawler, CSVwriter, builderconfig, configparser
#    except:
#      print("Unable to adjust sys.path")
#      raise ImportError('Error importing intakebuilder and other packages')
#      return -97
#  return True
     
def test_import1():
  import catalogbuilder
  assert catalogbuilder is not None
  
def test_import2():
  import catalogbuilder.intakebuilder
  assert catalogbuilder.intakebuilder is not None
  
def test_import3():
  from catalogbuilder.intakebuilder import gfdlcrawler, CSVwriter, configparser
  assert not None in [gfdlcrawler, CSVwriter, configparser]


