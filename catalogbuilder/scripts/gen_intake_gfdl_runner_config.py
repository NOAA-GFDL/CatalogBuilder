#!/usr/bin/env python

from catalogbuilder.scripts import gen_intake_gfdl
import sys, os 

#This is an example call to run catalog builder using a yaml config file.
package_dir = os.path.dirname(os.path.abspath(__file__))
configyaml = os.path.join(package_dir, 'configs/config-example.yml')

def create_catalog_from_config(config=configyaml):
    csv, json = gen_intake_gfdl.create_catalog(config=configyaml)
    return(csv,json)

