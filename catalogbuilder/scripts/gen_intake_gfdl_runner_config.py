#!/usr/bin/env python

from catalogbuilder.scripts import gen_intake_gfdl
import sys

#input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"
#output_path = "cftest"
config = configs/config-example.yml

try:
  gen_intake_gfdl.create_catalog(configyaml=config)
except:
  sys.exit("Exception occured calling gen_intake_gfdl.create_catalog")
  
