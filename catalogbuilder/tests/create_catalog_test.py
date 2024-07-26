#!/usr/bin/env python

from catalogbuilder.scripts import gen_intake_gfdl
#from . import gen_intake_gfdl
import sys
#the following line is to generate sample data, remove it as needed in your runscript
import make_sample_data

@pytest.mark.skip
def create_catalog(sample=True):
  if(sample == True): #create sample data 
      make_sample_data.make_sample_data()
  with TemporaryDirectory() as tmp:
        chdir(Path(tmp))
        input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"
        output_path = "test"
        try:
           json, csv = gen_intake_gfdl.create_catalog(input_path,output_path)
        except:
           sys.exit("Exception occured calling gen_intake_gfdl.create_catalog")
        create_data_catalog(path)
        json, csv = Path(f"{output}.json").resolve(), Path(f"{output}.csv").resolve()

 try:
       assert not None in [csv,json]

