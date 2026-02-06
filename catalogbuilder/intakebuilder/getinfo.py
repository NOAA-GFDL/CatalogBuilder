import sys
import pandas as pd
pd.options.mode.chained_assignment = None
import csv
from csv import writer
import os
import xarray as xr
from . import configparser
import yaml 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import logging
logger = logging.getLogger(__name__)

'''
getinfo.py provides helper functions to get information (from filename, DRS, file/global attributes) needed to populate the catalog
'''
def getProject(projectdir,dictInfo):
    '''
    return Project name from the project directory input
    :type dictInfo: object
    :param drsstructure:
    :return: dictionary with project key
    '''
    if "archive" in projectdir or "pp" in projectdir: 
       project = "dev" 
       dictInfo["activity_id"]=project
    return dictInfo

def getinfoFromYAML(dictInfo,yamlfile,miptable=None):
    with open(yamlfile) as f:
        mappings = yaml.load(f, Loader=yaml.FullLoader)
        if miptable:
            try:
                dictInfo["frequency"] = mappings[miptable]["frequency"]
            except KeyError:
                dictInfo["frequency"] = "NA"
            try:
                dictInfo["realm"] = mappings[miptable]["realm"]
            except KeyError:
                dictInfo["realm"]  = "NA"
    return dictInfo

def getFreqFromYAML(yamlfile,gfdlfreq=None):
    #returns cmip freq for gfdl pp freq 
    cmipfreq = None
    with open(yamlfile) as f:
        mappings = yaml.load(f, Loader=yaml.FullLoader)
        if gfdlfreq:
            try:
                cmipfreq = mappings[gfdlfreq]["frequency"]
            except KeyError:
                cmipfreq = None 
    return cmipfreq

def getStem(dirpath,projectdir):
    '''
    return stem from the project directory passed and the files crawled within
    :param dirpath:
    :param projectdir:
    :param stem directory:
    :return:
    '''
    stemdir = dirpath.split(projectdir)[1].split("/")  # drsstructure is the root
    return stemdir


def getInfoFromFilename(filename,dictInfo):
    # 5 AR: WE need to rework this, not being used in gfdl set up  get the following from the netCDF filename e.g.rlut_Amon_GFDL-ESM4_histSST_r1i1p1f1_gr1_195001-201412.nc
    if filename.endswith(".nc"):
        ncfilename = filename.split(".")[0].split("_")
        varname = ncfilename[0]
        dictInfo["variable_id"] = varname
        table_id = ncfilename[1]
        dictInfo["table_id"] = table_id 
        modelname = ncfilename[2]
        dictInfo["source_id"] = modelname
        expname = ncfilename[3]
        dictInfo["experiment_id"] = expname
        ens = ncfilename[4]
        dictInfo["member_id"] = ens
        grid = ncfilename[5]
        dictInfo["grid_label"] = grid
        try:
           tsubset = ncfilename[6]
        except IndexError:
           tsubset = "null" #For fx fields
        dictInfo["time_range"] = tsubset
    else:
        logger.debug("Filename not compatible with this version of the builder:"+filename)
    return dictInfo

#adding this back to trace back some old errors
def getInfoFromGFDLFilename(filename,dictInfo,configyaml):
    # 5 AR: get the following from the netCDF filename e.g. atmos.200501-200912.t_ref.nc
  if filename.endswith(".nc"): 
    stemdir = filename.split(".")
    #lets go backwards and match given input directory to the template, add things to dictInfo
    j = -2
    cnt = 1 #'variable_id': 'static', 'time_range': 'land'}
    if configyaml:
        input_file_template = configyaml.input_file_template
    else:
            logger.debug("No input_path_template found. Check configuration. Please open an issue with details if problem persists.Exiting")
            raise AttributeError("No input_path_template found. Check configuration. Please open an issue with details if problem persists.Exiting")
    if ".static" in filename :
        ## For static we handle this differently . The GFDL PP expected pattern is atmos.static.nc
        #TODO error checking as needed
        input_file_template = ['realm','NA'] 
        dictInfo["variable_id"] = "fixed" 
        dictInfo["frequency"] = "fx"
    nlen = len(input_file_template)
    for i in range(nlen-1,-1,-1): #nlen = 3
      try:
          if input_file_template[i] != "NA":
              try:
                  dictInfo[input_file_template[i]] = stemdir[(j)]
              except IndexError:
                  dictInfo[input_file_template[i]] = ""
      except IndexError:
          raise IndexError("oops in getInfoFromGFDLFilename"+str(i)+str(j)+input_file_template[i]+stemdir[j])
      j = j - 1
    cnt = cnt + 1

    if ".static" in filename:
        if "ocean" in dictInfo["realm"]:
          dictInfo["table_id"] = "Ofx"
        else:
          dictInfo["table_id"] = "fx"
    return dictInfo

def getRealm(dictInfo):
     realm = ""
     if (dictInfo["source_id"] == "cam"):
         realm = "atmos"
         dictInfo["realm"] = realm
     return(dictInfo)

def getInfoFromGFDLDRS(dirpath,projectdir,dictInfo,configyaml,variable_id):
    '''
    Returns info from project directory and the DRS path to the file
    :param dirpath:
    :param drsstructure:
    :param variable_id to check for static
    :return:
    '''
   # we need thise dict keys "project", "institute", "model", "experiment_id",
   #               "frequency", "realm", "mip_table",
   #               "ensemble_member", "grid_label", "variable",
   #               "temporal subset", "version", "path"]
 
   #Grab values based on their expected position in path 
    stemdir = dirpath.split("/")
    stemdir = dirpath.split("/")

    #lets go backwards and match given input directory to the template, add things to dictInfo
    j = -1
    cnt = 1
    if configyaml:
        input_path_template = configyaml.input_path_template
    else:
            logger.debug("No input_path_template found in config yaml. Check configuration, open a github issue with details if problem persists. ")
            raise AttributeError("No input_path_template found in config yaml. Check configuration, open a github issue with details if problem persists. ")
    #If variable_id is fixed, it's a GFDL PP static dataset and the input path template in config is aligned only up to a particular directory structure as this does not have the ts and frequency or time chunks 
    if variable_id == "fixed" :
        input_path_template = input_path_template[:-3 or None]
    nlen = len(input_path_template) 
    for i in range(nlen-1,0,-1):
      try:
          if input_path_template[i] != "NA":
              try:
                  dictInfo[input_path_template[i]] = stemdir[(j)]
              except IndexError:
                  raise IndexError("Check configuration. Is input path template set correctly?")
      except IndexError:
          raise IndexError("oops in getInfoFromGFDLDRS"+str(i)+str(j)+input_path_template[i]+stemdir[j])
      j = j - 1
    cnt = cnt + 1
    # WE do not want to work with anything that's not time series
    #TODO have verbose option to print message
    #TODO Make this elegant and intuitive 
    #TODO logger messages, not print 
    if "cell_methods" in dictInfo.keys():
      if dictInfo["cell_methods"] == "av":
         logger.info("Skipping time-average data")
         return {}
      elif dictInfo["cell_methods"] == "ts":
         logger.debug("time-series data")
      else: 
         logger.debug("This is likely static")
         dictInfo["cell_methods"] = ""
         dictInfo["member_id"] = "" 
    #CAM ESM: If realm is empty, ensure if there is a helper utility to populate this
     
      if("realm" not in dictInfo.keys()):
         dictInfo = getRealm(dictInfo)
    return dictInfo

def getInfoFromDRS(dirpath,projectdir,dictInfo):
    '''
    Returns info from project directory and the DRS path to the file
    :param dirpath:
    :param drsstructure:
    :return:
    '''
    stemdir = dirpath.split(projectdir)[1].split("/")  # drsstructure is the root
    try:
        institute = stemdir[2]
    except:
        institute = "NA"
    try:
        version = stemdir[9]
    except:
        version = "NA"
    dictInfo["institute"] = institute
    dictInfo["version"] = version
    return dictInfo
def return_xr(fname):
    filexr = (xr.open_dataset(fname))
    filexra = filexr.attrs
    return filexr,filexra
def getInfoFromVarAtts(fname,variable_id,dictInfo,att="standard_name",filexra=None):
    '''
    Returns info from the filename and xarray dataset object
    :param fname: filename
    :param filexr: Xarray dataset object
    :return: dictInfo with all variable atts 
    '''
    #try:
     
    filexr,filexra = return_xr(fname)
    if (dictInfo[att] == "na"):
      try:
          cfname = filexr[variable_id].attrs["standard_name"]
      except KeyError:
          cfname = "NA"
          try:
              long_name = filexr[variable_id].attrs["long_name"]
          except KeyError:
              long_name = "NA"
          cfname = long_name.replace(" ", "_")
      dictInfo["standard_name"] = cfname 
      logger.info(f"standard_name found: {dictInfo['standard_name']}")
    return dictInfo
def getInfoFromGlobalAtts(fname,dictInfo,filexra=None):
    '''
    Returns info from the filename and xarray dataset object
    :param fname: DRS compliant filename
    :param filexr: Xarray dataset object
    :return: dictInfo with institution_id version realm frequency and product
    '''
    filexra = return_xr(fname)
    if dictInfo["institute"] == "NA":
        try:
            institute = filexra["institution_id"]
        except KeyError:
          institute = "NA"
        dictInfo["institute"] = institute
    if dictInfo["version"] == "NA":
        try:
            version = filexra["version"]
        except KeyError:
            version = "NA"
        dictInfo["version"] = version
    realm = filexra["realm"]
    dictInfo["realm"] = realm
    frequency = filexra["frequency"]
    dictInfo["frequency"] = frequency
    return dictInfo

def getStandardName(list_variable_id,list_realm):
    '''
    Returns dict standard name for the variable in question
    '''
    unique_cf = "na"
    dictCF = {}
    try:
        url = "https://raw.githubusercontent.com/NOAA-GFDL/MDTF-diagnostics/refs/heads/main/data/gfdl-cmor-tables/gfdl_to_cmip5_vars.csv"
        url2 = "https://raw.githubusercontent.com/NOAA-GFDL/MDTF-diagnostics/refs/heads/main/data/gfdl-cmor-tables/gfdl_to_cmip6_vars.csv"
        df1 = pd.read_csv(url, sep=",", header=0,index_col=False)
        df2 = pd.read_csv(url2, sep=",", header=0,index_col=False)
        #TODO Add try catch except for concat operation if concat fails for some reason 
        df = pd.concat([df1,df2]).drop_duplicates().reset_index(drop=True)
    except IOError:
        raise IOError("Unable to open file")
  #search for variable and its cf name
    for variable_id in list_variable_id:
       for realm in list_realm: 
           cfname = df[(df['GFDL_varname'] == variable_id) & (realm in df['modeling_realm'])]["standard_name"]
           list_cfname = cfname.tolist()
           if len(list_cfname) == 0:
               cfname = (df[df['CMOR_varname'] == variable_id]["standard_name"])
               list_cfname = cfname.tolist()
           if len(list_cfname) > 0:
               unique_cf = list(set(list_cfname))[0]
               varrealm = "{0},{1}".format(variable_id,realm)
               dictCF[varrealm] = unique_cf
    return dictCF
