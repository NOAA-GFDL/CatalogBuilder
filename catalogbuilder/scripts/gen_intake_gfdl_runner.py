#!/usr/bin/env python

#TODO test after conda pkg is published and make changes as needed 
from catalogbuilder.scripts import gen_intake_gfdl
import sys
'''
input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"
output_path = "test"
try:
  gen_intake_gfdl.create_catalog(input_path,output_path)
except:
  sys.exit("Exception occured calling gen_intake_gfdl.create_catalog")

'''
#This is an example call to run catalog builder using a default yaml config file without explicit specifications
input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"
output_path = "default-mdtf-catalog"

def create_catalog_default(input_path=input_path,output_path=output_path):
    csv, json = gen_intake_gfdl.create_catalog(input_path=input_path,output_path=output_path)
    return(csv,json)

if __name__ == '__main__':
    create_catalog_default(input_path,output_path,configyaml)
    
