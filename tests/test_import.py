def check_import():
 try:
   from intakebuilder import gfdlcrawler, CSVwriter, configparser
   print("Imported intakebuilder, gfdlcrawler, CSVwriter, configparser")
   return True
 except ModuleNotFoundError:
    print("The module intakebuilder is not installed. Do you have intakebuilder in your sys.path or have you activated the conda environment with the intakebuilder package in it? ")
    print("Attempting again with adjusted sys.path ")
    try:
       sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except:
       print("Unable to adjust sys.path")
    #print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from intakebuilder import gfdlcrawler, CSVwriter, builderconfig, configparser
        print("Imported, and relied on sys.path")
        return True
    except ModuleNotFoundError:
        print("The module 'intakebuilder' is still not installed. Do you have intakebuilder in your sys.path or have you activated the conda environment with the intakebuilder package in it? ")
        raise ImportError('Error importing intakebuilder and other packages')
        return -97
     
def test_import():
    assert check_import() == True


