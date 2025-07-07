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
def main(json_path=None):

    ''' This test validates catalogs against CMIP6 or GFDL controlled vocabulary (CV) as provided by particular JSON schemas per vocabulary type. CMIP6 CV's are found in the WCRP-CMIP/CMIP6_CVs github repository. GFDL CV's are found in the NOAA-GFDL/CMIP6_CVs github repository.

     JSON_PATH = Path to generated catalog JSON schema
     CV_DIR_PATH = Path to CMIP6 CV Repository.

     USAGE:
         To validate against GFDL CV's: compval <json_path>
         (Uses CV found in json's "vocabulary" field) '''


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
    for attribute in j["attributes"]:

        #Checks to see if the vocabulary field is filled out. If so, use the vocab. Also, we avoid chunk_freq because it's currently broken.
        try:
            if 'chunk_freq' not in attribute["column_name"] and attribute["vocabulary"]:
                cv_url = attribute["vocabulary"]
                logger.info("Validating " + attribute["column_name"] + " vocabulary")
            else:
                continue
        except KeyError:
            logger.warn("Missing vocabulary field in catalog schema")

        try:
            with urllib.request.urlopen(cv_url) as f:
                json_data = json.load(f)
        except:
            raise IOError("Unable to open json: " + str(list(attribute.values())[0]))

        #This will probably break if formatting is different. Will adjust if necessary.
        try:
            for cv in json_data[attribute['column_name']].keys():
                vocab_list.append(cv)
        except AttributeError:
            for cv in json_data[attribute['column_name']]:
                vocab_list.append(cv)

        #Look for "bad vocab" in the CSV
        for vocab in catalog[list(attribute.values())[0]]:
            if vocab not in vocab_list and vocab not in bad_vocab:
                if not isinstance(vocab,str) and math.isnan(vocab):
                    continue
                else:
                    #Update the bad vocabulary dictionary (column name has to be value because we can't have duplicate keys)
                    bad_vocab.update({vocab:attribute['column_name']})
                    #We keep track of all the urls users need to correct their bad vocabulary
                    if attribute['column_name'] not in urls:
                        urls.update({attribute['column_name']:cv_url})

    if nan_list:
        logger.warn("WARNING: NaN's found in: " + str(nan_list))

    if bad_vocab:
        for entry in bad_vocab:
            logger.error("Inconsistent " + bad_vocab[entry] + " value: " + '"' + entry + '"')
        for entry in urls:
            logger.info("Compliant " + entry + " vocabulary can be found here: " + urls[entry])
        raise ValueError("Found inconsistent value(s)")
    else:
        logger.info("Check passed.")
        return

if __name__ == '__main__':
    main()
