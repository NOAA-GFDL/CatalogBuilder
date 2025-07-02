#!/usr/bin/env python

import click
import json
from jsondiff import diff
import pandas as pd
import sys
import os
import re
import math
import logging
import urllib.request

logger = logging.getLogger('local')
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout)

@click.command()
@click.argument('json_path',nargs=1,required=True)
@click.argument('cv_dir_path',nargs=1,required=False)
def main(json_path=None, cv_dir_path=None):

    ''' This test validates catalogs against CMIP6 or GFDL controlled vocabulary (CV) as provided by particular JSON schemas per vocabulary type. CMIP6 CV's are found in the WCRP-CMIP/CMIP6_CVs github repository. GFDL CV's are found in the NOAA-GFDL/CMIP6_CVs github repository.

     JSON_PATH = Path to generated catalog JSON schema
     CV_DIR_PATH = Path to CMIP6 CV Repository.

     USAGE:
         To validate against GFDL CV's: compval <json_path>
         (Uses CV found in json's "vocabulary" field)

         To validate against CMIP CV's: compval <json_path> <cv_dir_path>
         (Must clone WCRP-CMIP/CMIP6_CVs github directory. CV is found automatically given the path to this directory) '''
    bad_vocab = {}
    nan_list = []
    vocab_list = []
    urls = {}

    #Open catalog json
    try:
        j = json.load(open(json_path))
    except:
        raise IOError("Unable to open file. Is this the generated catalog json file?")

    #Get CSV from JSON and open it
    csv_path = str(j["catalog_file"])
    catalog = pd.read_csv(csv_path)

    #Parse through the JSON and find which CV is needed
    for x in j["attributes"]:

        #Checks to see if the vocabulary field is filled out. If so, use the vocab. Also, we avoid chunk_freq because it's currently broken.
        try:
            if 'chunk_freq' not in x["column_name"] and x["vocabulary"]:
                cv_url = x["vocabulary"]
                logger.info("Validating " + x["column_name"] + " vocabulary")
            else:
                continue
        except KeyError:
            logger.warn("Missing vocabulary field in catalog schema")

        try:
            with urllib.request.urlopen(cv_url) as f:
                json_data = json.load(f)
        except:
            raise IOError("Unable to open json: " + str(list(x.values())[0]))

        #This will probably break if formatting is different. Will adjust if necessary.
        try:
            for y in json_data[x['column_name']].keys():
                vocab_list.append(y)
        except AttributeError:
            for y in json_data[x['column_name']]:
                vocab_list.append(y)

        #Look for "bad vocab" in the CSV
        for z in catalog[list(x.values())[0]]:
            if z not in vocab_list and z not in bad_vocab:
                if not isinstance(z,str) and math.isnan(z):
                    continue
                else:
                    #Update the bad vocabulary dictionary (column name has to be value because we can't have duplicate keys)
                    bad_vocab.update({z:x['column_name']})
                    #We keep track of all the urls users need to correct their bad vocabulary
                    if x['column_name'] not in urls:
                        urls.update({x['column_name']:cv_url})

    if nan_list:
        logger.warn("WARNING: NaN's found in: " + str(nan_list))

    if bad_vocab:
        for entry in bad_vocab:
            logger.error("Inconsistent " + bad_vocab[entry] + " value: " + '"' + entry + '"')
        for entry in urls:
            logger.info("Compliant " + entry + " vocabulary can be found here: " + urls[entry])
        raise ValueError("Found inconsistent value(s): ")
    else:
        logger.info("Check passed.")
        return

if __name__ == '__main__':
    main()
