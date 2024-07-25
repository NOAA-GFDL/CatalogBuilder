#!/usr/bin/env python

#from catalogbuilder.scripts import gen_intake_gfdl
from . import gen_intake_gfdl
import sys

# this will break at some point #TODO
sys.argv = ['input_path','--config', '/home/a1r/github/CatalogBuilder/scripts/configs/config-example.yml']
print(sys.argv)
gen_intake_gfdl.main()

