import os,sys
def check_import():
 try:
   from intakebuilder import gfdlcrawler, CSVwriter, configparser
 except ImportError:
    print("The module intakebuilder is not installed. Do you have intakebuilder in your sys.path or have you activated the conda environment with the intakebuilder package in it? ")
    print("Attempting again with adjusted sys.path ")
    try:
       #candobetter with actual conda package built before this, but this is a decent test for those that do not use conda package
       sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/catalogbuilder")
       from intakebuilder import gfdlcrawler, CSVwriter, builderconfig, configparser
    except:
       print("Unable to adjust sys.path")
       raise ImportError('Error importing intakebuilder and other packages')
       return -97
 return True
     
def test_import():
    assert check_import() == True


