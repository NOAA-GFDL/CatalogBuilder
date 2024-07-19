#!/usr/bin/env python

from scripts import gen_intake_gfdl
import sys

sys.argv = ['input_path','--config', '/home/a1r/github/CatalogBuilder/scripts/configs/config-example.yml']
print(sys.argv)
gen_intake_gfdl.main()

