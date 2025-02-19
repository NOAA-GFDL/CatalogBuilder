#!/usr/bin/env python

import click
import json
from jsondiff import diff
import pandas as pd
import sys
import os
import re
import math

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
    bad_vocab = []
    nan_list = []
    vocab_list = []

    #Open catalog json
    j = json.load(open(json_path))

    #Get CSV from JSON and open it
    csv_path = str(j["catalog_file"])
    catalog = pd.read_csv(csv_path)

    if cv_dir_path:
    #Gather all CV's from CMIP6_CV Dir
        for filename in os.listdir(cv_dir_path):
            if str(filename).startswith("CMIP6"):
                cv_type = re.search('CMIP6_(.*).json',str(filename)).group(1)

                #Open JSON
                try:
                    cv = json.load(open(cv_dir_path+'/CMIP6_'+cv_type+'.json'))
                except:
                    sys.exit("Unable to open json: " + cv_type)

                #Ignoring directory structure for now
                if list(cv.keys())[0] == 'DRS':
                    continue
                    #vals = list(cv.values())
                    #dir_structure = list(vals[0].values())[2]

                else:
                    vals = list(cv.values())

                    #Sometimes the CV formats are a little different :)
                    if isinstance(vals[0],list):
                        for vocab in vals[0]:
                            vocab_list.append(vocab)

                    else: 
                        for vocab in vals[0].keys():
                            vocab_list.append(vocab)
                  
                #Sometimes our catalogs don't include the cv type as a column
                if cv_type in catalog:

                    for y in catalog[cv_type]:

                        #If there's NaN's this whole thing will break so let's get those out of the way
                        if not isinstance(y,str) and math.isnan(y):
                            #Add to the nan list 
                            if cv_type not in nan_list:
                                nan_list.append(cv_type)
                                continue
                            else:
                                continue

                        #Check for bad vocab
                        if y not in vocab_list and y not in bad_vocab:
                            bad_vocab.append(y)

    else:
        #Parse through the JSON and find which CV is needed

        for x in j["attributes"]:

            #Checks to see if the vocabulary field is filled out. If so, use the vocab. Also, we avoid chunk_freq because it's currently broken.
            if list(x.values())[1]:
                cv_url = list(x.values())[1]
                try:
                    df = pd.read_json(cv_url)
                except:
                    sys.exit("Unable to open json: " + list(x.values())[0])

                #This will probably break if formatting is different. Will adjust if necessary.
                for y in df[list(x.values())[0]].keys():
                    vocab_list.append(y)

                #Look for "bad vocab" in the CSV
                for z in catalog[list(x.values())[0]]:
                    if z not in vocab_list and z not in bad_vocab:
                        if not isinstance(z,str) and math.isnan(z):
                            continue
                        else:
                             bad_vocab.append(z)

    if nan_list:
        print("WARNING: NaN's found in: " + str(nan_list))

    if bad_vocab:
        print("Found inconsistent value(s): " + str(bad_vocab))
    else:
        print("Check passed.")

if __name__ == '__main__':
    main()

