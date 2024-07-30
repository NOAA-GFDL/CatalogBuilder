#!/usr/bin/env python

from catalogbuilder.scripts import gen_intake_gfdl
import sys

#This is an example call to run catalog builder using a yaml config file.

configyaml = os.path.join(package_dir, '../configs/config-example.yml')"

def create_catalog_from_config(config=configyaml):
    gen_intake_gfdl.create_catalog(config=configyaml)

