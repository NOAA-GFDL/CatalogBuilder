#!/usr/bin/env python

import json
import sys,pandas as pd
import click
import os
from pathlib import Path
import logging

logger = logging.getLogger('local')
logger.setLevel(logging.INFO)
logging.basicConfig(stream=sys.stdout)

try:
   from catalogbuilder.intakebuilder import gfdlcrawler, CSVwriter, builderconfig, configparser, getinfo
except ModuleNotFoundError:
    print("The module intakebuilder is not installed. Do you have intakebuilder in your sys.path or have you activated the conda environment with the intakebuilder package in it? ")
    print("Attempting again with adjusted sys.path ")
    try:
       sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except:
       print("Unable to adjust sys.path")
    #print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from intakebuilder import gfdlcrawler, CSVwriter, builderconfig, configparser,getinfo
        print(gfdlcrawler.__file__)
    except ModuleNotFoundError:
        sys.exit("The module 'intakebuilder' is still not installed. Do you have intakebuilder in your sys.path or have you activated the conda environment with the intakebuilder package in it? ")

package_dir = os.path.dirname(os.path.abspath(__file__))
#template_path = os.path.join(package_dir, '../cats/gfdl_template.json')

def create_catalog(input_path=None, output_path=None, config=None, filter_realm=None, filter_freq=None, filter_chunk=None,
         overwrite=False, append=False, slow = False, verbose=False):
    if verbose:
       logger.setLevel(logging.DEBUG)
       logger.info("Verbose log activated.")
    else:
       logger.setLevel(logging.INFO)
       logger.info("[Mostly] silent log activated")
    configyaml = None
    # TODO error catching
    if (config is not None):
        configyaml = configparser.Config(config,logger)
    else:
            # If user does not pass a config, we will use the default config with the same format to avoid special cases
        #
         try:
                  pkg = importlib_resources.files("catalogbuilder.scripts")
                  config_path = pkg / "configs" / "config.yaml"
                  logger.info("Default config path activated from package resources configs/config.yaml")
         except:
                 try:
                    config_path = os.path.join(package_dir, 'configs/config.yaml')
                    logger.info("Default config path activated from path configs/config.yaml")
                 except:
                    sys.exit("Can't locate or read config, check --config ")
         configyaml = configparser.Config(config,logger) 
         if(input_path is None):     
            input_path = configyaml.input_path
         if(output_path is None):
            output_path = configyaml.output_path
    if((input_path is None) or (output_path is None)):
       sys.exit("Missing: input_path or output_path. Pass it in the config yaml or as command-line option")     
    if config is None or not configyaml.schema:
            logger.info("Default schema: catalogbuilder/cats/gfdl_template.json")
            template_path = os.path.join(package_dir, '../cats/gfdl_template.json')
    else:
            template_path = configyaml.schema
            print("Using schema from config file", template_path)
    if not os.path.exists(input_path):
        sys.exit("Input path does not exist. Adjust configuration.")
    if not os.path.exists(Path(output_path).parent.absolute()):
        sys.exit("Output path parent directory does not exist. Adjust configuration.")
    logger.info("input path: "+ input_path)
    logger.info( " output path: "+ output_path)
    project_dir = input_path
    csv_path = "{0}.csv".format(output_path)
    json_path = "{0}.json".format(output_path) 

    ######### SEARCH FILTERS ###########################

    dictFilter = {}
    dictFilterIgnore = {}
    if filter_realm:
        dictFilter["modeling_realm"] = filter_realm
    if filter_freq:
        dictFilter["frequency"] = filter_freq
    if filter_chunk:
        dictFilter["chunk_freq"] = filter_chunk

    ''' Override config file if necessary for dev
    project_dir = "/archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_1pctCO2_D1/gfdl.ncrc4-intel16-prod-openmp/pp/"
    #for dev csvfile =  "/nbhome/$USER/intakebuilder_cats/intake_gfdl2.csv" 
    dictFilterIgnore = {}
    dictFilter["modeling_realm"]= 'atmos_cmip'
    dictFilter["frequency"] = "monthly"
    dictFilter["chunk_freq"] = "5yr"
    dictFilterIgnore["remove"]= 'DO_NOT_USE'
    '''
    dictInfo = {}
    project_dir = project_dir.rstrip("/")
    logger.debug("Calling gfdlcrawler.crawlLocal")
    list_files = gfdlcrawler.crawlLocal(project_dir, dictFilter, dictFilterIgnore, logger, configyaml,slow)
    #Grabbing data from template JSON, changing CSV path to match output path, and dumping data in new JSON
    with open(template_path, "r") as jsonTemplate:
        data = json.load(jsonTemplate)
        data["catalog_file"] = os.path.abspath(csv_path)
    jsonFile = open(json_path, "w")
    json.dump(data, jsonFile, indent=2)
    jsonFile.close()
    headers = CSVwriter.getHeader(configyaml)

    # When we pass relative path or just the filename the following still needs to not choke
    # so we check if it's a directory first
    if os.path.isdir(os.path.dirname(csv_path)):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    CSVwriter.listdict_to_csv(list_files, headers, csv_path, overwrite, append,slow)
    df = None
    if(slow == False) & ('standard_name' in headers ):
               #If we badly need standard name, we use gfdl cmip mapping tables especially when one does not prefer the slow option. Useful for MDTF runs
                      df = pd.read_csv(os.path.abspath(csv_path), sep=",", header=0,index_col=False)
                      list_variable_id = []
                      try:
                          list_variable_id = df["variable_id"].unique().tolist()
                      except:
                          print("Having trouble finding 'variable_id'... Be sure to add it to the output_path_template field of your configuration")
                      try:
                          list_realm = df["realm"].unique().tolist()
                      except:
                          print("Having trouble finding 'realm'... Be sure to add it to the output_path_template field of your configuration")
                      dictVarCF = getinfo.getStandardName(list_variable_id,list_realm)
                      #print("standard name from look-up table-", dictVarCF)
                      for k, v in dictVarCF.items():
                        try:
                           var = k.split(",")[0]
                        except ValueError:
                           continue
                        try:
                           realm = k.split(",")[1]
                        except ValueError:
                           continue 
                        if(var is not None) & (realm is not None):
                            df['standard_name'].loc[(df['variable_id'] == var) & (df['realm'] == realm) ] = v
                        #df['standard_name'].loc[(df['variable_id'] == k)] = v
    if(slow == False) & ('standard_name' in headers):
       if ((df is not None) & (len(df) != 0) ):
           with open(csv_path, 'w') as csvfile:
               df.to_csv(csvfile,index=False)

    print("JSON generated at:", os.path.abspath(json_path))
    print("CSV generated at:", os.path.abspath(csv_path))
    logger.info("CSV generated at" + os.path.abspath(csv_path))
    return(csv_path,json_path)

#Setting up argument parsing/flags
@click.command()
#TODO arguments dont have help message. So consider changing arguments to options?
@click.argument('input_path',required=False,nargs=1)
#,help='The directory path with the datasets to be cataloged. E.g a GFDL PP path till /pp')
@click.argument('output_path',required=False,nargs=1)
#,help='Specify output filename suffix only. e.g. catalog')
@click.option('--config',required=False,type=click.Path(exists=True),nargs=1,help='Path to your yaml config, Use the config_template in intakebuilder repo')
@click.option('--filter_realm', nargs=1)
@click.option('--filter_freq', nargs=1)
@click.option('--filter_chunk', nargs=1)
@click.option('--overwrite', is_flag=True, default=False)
@click.option('--append', is_flag=True, default=False)
@click.option('--slow','-s', is_flag=True, default=False, help='This option looks up standard names in netcdf file to fill up the standard name column if its present in the header specs. If standard_name is absent, long_name with space replaced by underscore is utilized')
@click.option('--verbose/--silent', default=False, is_flag=True) #default has silent option. Use --verbose for detailed logging

def create_catalog_cli(**kwargs):
    return create_catalog(**kwargs)
                          
if __name__ == '__main__':
    create_catalog_cli()
