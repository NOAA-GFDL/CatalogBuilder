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
from importlib.resources import files
import urllib.request

logger = logging.getLogger(__name__)

@click.command()
@click.argument('json_path',nargs=1,required=True)
@click.argument('json_template_path', nargs = 1 , required = False)
@click.option('--vocab', is_flag=True, default = False, help="Validates catalog vocabulary")
@click.option('-pg','--proper_generation', is_flag=True, default = False, help="Validates that catalog has been 'properly generated' (No empty columns, reflects template)")
@click.option('-tf', '--test_failure', is_flag=True, default = False, help="Errors are only printed. Program will not exit.")

def main(json_path: str,json_template_path: str, vocab: bool, proper_generation: bool, test_failure: bool):

    ''' The catalog validator supports two independent test modes that can be run together or separately.

     Vocabulary (CV) testing (--vocab flag):
         Checks each catalog value against the controlled vocabularies (CVs) defined in the catalog
         schema's vocabulary section. CMIP6 CVs are fetched from the WCRP-CMIP/CMIP6_CVs GitHub
         repository; GFDL CVs are fetched from the NOAA-GFDL/CMIP6_CVs GitHub repository.

     Proper generation / completeness testing (-pg / --proper_generation flag):
         Checks that the catalog was built correctly: the JSON descriptor matches the expected
         template, the CSV contains at least one data row, and every required column (from
         groupby_attrs) exists and has no empty values. Use -tf / --test-failure to log errors
         without raising exceptions (useful for expected failures in CI).

     Usage:
         compval.py <json_path> --vocab
         compval.py <json_path> --proper_generation
         compval.py <json_path> <json_template_path> --proper_generation
         (Both flags can be combined in a single call.)
    '''

    return compval(json_path,json_template_path, vocab, proper_generation, test_failure)

def compval(json_path,json_template_path, vocab, proper_generation, test_failure):
    """ Validates a generated intake-ESM catalog located at json_path.

    When vocab is True, each catalog value is checked against the controlled vocabularies
    referenced in the catalog schema. When proper_generation is True, the catalog JSON is
    compared against the template at json_template_path (or the default GFDL template), the
    CSV is checked for at least one data row, and all required columns are checked for missing
    values. When test_failure is True, validation errors are logged as warnings instead of
    raising exceptions.

    Raises IOError if any file cannot be opened, ValueError if required columns are missing or
    values are invalid, and Exception if other validation errors are found.
    """
    #Open catalog json
    try:
        j = json.load(open(json_path))
    except:
        raise IOError("Unable to open file. Is this the generated catalog json file?")

    # VOCABULARY VALIDATION IS DONE HERE
    if vocab:

        bad_vocab = {}
        nan_list = []
        vocab_list = []
        urls = {}
    
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
                logger.warning("Missing vocabulary field in catalog schema")

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
            for _vocab in catalog[list(attribute.values())[0]]:
                if _vocab not in vocab_list and _vocab not in bad_vocab:
                    if not isinstance(_vocab,str) and math.isnan(_vocab):
                        continue
                    else:
                        #Update the bad vocabulary dictionary (column name has to be value because we can't have duplicate keys)
                        bad_vocab.update({_vocab:attribute['column_name']})
                        #We keep track of all the urls users need to correct their bad vocabulary
                        if attribute['column_name'] not in urls:
                            urls.update({attribute['column_name']:cv_url})

        if nan_list:
            logger.warning("WARNING: NaN's found in: " + str(nan_list))

        if bad_vocab:
            for entry in bad_vocab:
                if not entry == list(bad_vocab.keys())[-1]:
                    logger.error("Inconsistent " + bad_vocab[entry] + " value: " + '"' + entry + '"')
                    continue
                logger.error("Inconsistent " + bad_vocab[entry] + " value: " + '"' + entry + '"\n')
            for entry in urls:
                logger.info("Compliant " + entry + " vocabulary can be found here: " + urls[entry])
            if not test_failure:
                raise ValueError("Found inconsistent value(s)")
            logger.warning("Found inconsistent value(s)\n")
        else:
            logger.info("Check passed.")

    # COMPLETENESS/SCHEMA REFLECTION VALIDATION IS DONE HERE
    if proper_generation:

        if json_template_path:
            json_template = json.load(open(json_template_path))
        else:
            jpath = files('catalogbuilder').joinpath('cats/gfdl_template.json')
            json_template = json.load(open(jpath)) 

        #Validate JSON against JSON template
        comp = (diff(j,json_template))
        for key in comp.keys():
            if key != 'catalog_file':
                if test_failure:
                    logger.warning(key + ' section of JSON does not refect template')
                else:
                    raise ValueError(key + ' section of JSON does not refect template')

        #Get CSV from JSON and open it
        csv_path = j["catalog_file"]
        catalog = pd.read_csv(csv_path)

        if len(catalog.index) < 1:
            if test_failure:
                logger.warning("Catalog has no values")
            else:
                raise ValueError("Catalog has no values")

        #Get required columns
        req = (j["aggregation_control"]["groupby_attrs"])

        #Check the csv headers for required columns/values
        errors = 0
        for column in req:
            if column not in catalog.columns:
                logger.error("The required column '" + column + "' does not exist in the csv. In other words, there is some inconsistency between the json and the csv file. Please check out info listed under aggregation_control and groupby_attrs in your json file and verify if those columns show up in the csv as well.")
                errors += 1

            if column in catalog.columns:
                if catalog[column].isnull().values.any():
                    logger.error("'" + column + "' contains empty values.")
                    errors += 1

        if errors > 0:
            if test_failure:
                logger.warning("Found " + str(errors) + " errors.")
            else:
                raise Exception("Found " + str(errors) + " errors.")

    else:
        logger.info("No tests ran. Please use either --vocab or -pg/--proper_generation flags for testing")
    return

if __name__ == '__main__':
    main()
