#!/usr/bin/env python

from catalogbuilder.scripts import gen_intake_gfdl
import sys

#This is an example call to run catalog builder using a yaml config file.

configyaml = os.path.join(package_dir, '../configs/config-example.yml')"
gen_intake_gfdl.create_catalog(config=configyaml)

#to output success/failure 

csv = "/home/runner/work/forkCatalogBuilder-/sample-mdtf-catalog.csv"
json = "/home/runner/work/forkCatalogBuilder-/sample-mdtf-catalog.json"

csvpath = Path(csv)
jsonpath = Path(json)

assert csvpath.is_file()
assert csvpath.is_file()

