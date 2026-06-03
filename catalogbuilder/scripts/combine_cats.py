#!/usr/bin/env python

import pandas as pd
import json
from jsondiff import diff
import pathlib
import sys 
import os, click

import logging
logger = logging.getLogger(__name__)

@click.command()
@click.option('-i','--inputfiles',required=True,multiple=True,help='Pass json catalog files to-be-combined, space separated')
@click.option('-o','--output_path',required=True,nargs=1,help='Specify the output json path')

#Assume csv is in the same path and deduce the filename
def combine_cats(inputfiles,output_path):
    """Combines two intake-ESM JSON catalogs and their associated CSV files into a single catalog.

    Reads the two JSON catalog descriptors identified by inputfiles, verifies that their schemas
    are compatible (only the catalog_file field differs), concatenates the two CSV files, and
    writes a new merged CSV and a new JSON descriptor to combined_json. Usage example:
    combine_cats.py -i catalog1.json -i catalog2.json -o combined.json
    """

    try:
       json1 = inputfiles[0]
    except:
       raise IndexError("cannot parse inputfiles")
    try:
       json2 = inputfiles[1]
    except:
       raise IndexError("cannot parse inputfiles2")
    try:
       combined_json = output_path
    except:
       raise IndexError("cannot parse output_path")
    p1 = pathlib.PurePath(json1)
    csv1 =  p1.with_suffix('.csv')
    logger.debug(f"{csv1}")
    p2 = pathlib.Path(json2)
    csv2 = p2.with_suffix('.csv')
    logger.debug(f"{csv2}")

    cat_csvs = [csv1,csv2] #TODO check for valid paths, pass it with cmd line if necessary 

    #####Check if the schema is the same
    with open(json1) as f1, open(json2) as f2:
        json_obj1 = json.load(f1)
        json_obj2 = json.load(f2) 
    differ = diff(json_obj1, json_obj2) 
    logger.info("Schema differs")
    logger.info("{differ}")
    if len(differ.keys()) == 1:
        if "catalog_file" in differ.keys():
            logger.info("We can combine since the catalog_file is the only difference")
    else:
        logger.info("Schema likely varies significantly, cannot combine")
        raise RuntimeError("Schema likely varies significantly, cannot combine")

    #### If the headers are the same, append the data frames together and create the combined csv 
    p3 = pathlib.Path(combined_json)
    combined_csv = p3.with_suffix('.csv')

    df_concat = pd.concat([pd.read_csv(f) for f in cat_csvs], ignore_index = True)
    df_concat.to_csv(combined_csv, index=False)

    #Write out a catalog specification 
    f = open(json1)
    catspec = json.load(f)
    for catalog_file in catspec['catalog_file']:
       catspec['catalog_file'] = os.fspath(combined_csv)

    #Write out the combined json  
    json_data = json.dumps(catspec,indent=4)
    with open(combined_json,'w') as outfile:
        outfile.write(json_data)

    #Print pointers 
    logger.info("Combined catalog specification: {combined_json}")
    logger.info("Combined csv/catalog: {combined_csv}")

def combine_cats_cli(**kwargs):
    return combine_cats(**kwargs)

if __name__ == '__main__':
    combine_cats_cli()
