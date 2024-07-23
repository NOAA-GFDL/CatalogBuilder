import sys
import pandas as pd
import csv
from csv import writer
import os
import xarray as xr
from intakebuilder import builderconfig, configparser 


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
    if ("archive" in projectdir or "pp" in projectdir): 
       project = "dev" 
       dictInfo["activity_id"]=project
    return dictInfo

def getinfoFromYAML(dictInfo,yamlfile,miptable=None):
    import yaml
    with open(yamlfile) as f:
        mappings = yaml.load(f, Loader=yaml.FullLoader)
        #print(mappings)
        #for k, v in mappings.items():
              #print(k, "->", v)
        if(miptable):
            try:
                dictInfo["frequency"] = mappings[miptable]["frequency"]
            except KeyError:
                dictInfo["frequency"] = "NA"
            try:
                dictInfo["realm"] = mappings[miptable]["realm"]
            except KeyError:
                dictInfo["realm"]  = "NA"
    return(dictInfo)

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


def getInfoFromFilename(filename,dictInfo,logger):
    # 5 AR: WE need to rework this, not being used in gfdl set up  get the following from the netCDF filename e.g.rlut_Amon_GFDL-ESM4_histSST_r1i1p1f1_gr1_195001-201412.nc
    #print(filename)
    if(filename.endswith(".nc")):
        ncfilename = filename.split(".")[0].split("_")
        varname = ncfilename[0]
        dictInfo["variable"] = varname
        miptable = ncfilename[1]
        dictInfo["mip_table"] = miptable
        modelname = ncfilename[2]
        dictInfo["model"] = modelname
        expname = ncfilename[3]
        dictInfo["experiment_id"] = expname
        ens = ncfilename[4]
        dictInfo["ensemble_member"] = ens
        grid = ncfilename[5]
        dictInfo["grid_label"] = grid
        try:
           tsubset = ncfilename[6]
        except IndexError:
           tsubset = "null" #For fx fields
        dictInfo["temporal_subset"] = tsubset
    else:
        logger.debug("Filename not compatible with this version of the builder:"+filename)
    return dictInfo

#adding this back to trace back some old errors
def getInfoFromGFDLFilename(filename,dictInfo,logger):
    # 5 AR: get the following from the netCDF filename e.g. atmos.200501-200912.t_ref.nc
    if(filename.endswith(".nc")): #and not filename.startswith(".")):
        ncfilename = filename.split(".")
        varname = ncfilename[-2]
        dictInfo["variable_id"] = varname
        #miptable = "" #ncfilename[1]
        #dictInfo["mip_table"] = miptable
        #modelname = ncfilename[2]
        #dictInfo["model"] = modelname
        #expname = ncfilename[3]
        #dictInfo["experiment_id"] = expname
        #ens = ncfilename[4]
        #dictInfo["ensemble_member"] = ens
        #grid = ncfilename[5]
        #dictInfo["grid_label"] = grid
        try:
           tsubset = ncfilename[1]
        except IndexError:
           tsubset = "null" #For fx fields
        dictInfo["temporal_subset"] = tsubset
    else:
        logger.debug("Filename not compatible with this version of the builder:"+filename)
    return dictInfo

def getInfoFromGFDLDRS(dirpath,projectdir,dictInfo,configyaml):
    '''
    Returns info from project directory and the DRS path to the file
    :param dirpath:
    :param drsstructure:
    :return:
    '''
   # we need thise dict keys "project", "institute", "model", "experiment_id",
   #               "frequency", "realm", "mip_table",
   #               "ensemble_member", "grid_label", "variable",
   #               "temporal subset", "version", "path"]
 
   #Grab values based on their expected position in path 
    stemdir = dirpath.split("/")
   # adding back older versions to ensure we get info from builderconfig
    stemdir = dirpath.split("/")

    #lets go backwards and match given input directory to the template, add things to dictInfo
    j = -1
    cnt = 1
    if configyaml:
        output_path_template = configyaml.output_path_template
    else:
        try:
            output_path_template = builderconfig.output_path_template 
        except:
            sys.exit("No output_path_template found in builderconfig.py. Check configuration.")

    nlen = len(output_path_template) 
    for i in range(nlen-1,0,-1):
      try:
          if(output_path_template[i] != "NA"):
              try:
                  dictInfo[output_path_template[i]] = stemdir[(j)]
              except IndexError:
                  print("Check configuration. Is output path template set correctly?")
                  exit()
      except IndexError:
          sys.exit("oops in getInfoFromGFDLDRS"+str(i)+str(j)+output_path_template[i]+stemdir[j])
      j = j - 1
    cnt = cnt + 1
    # WE do not want to work with anythi:1
    # ng that's not time series
    #TODO have verbose option to print message
    if "cell_methods" in dictInfo.keys():
      if (dictInfo["cell_methods"] != "ts"):
         #print("Skipping non-timeseries data")
         return {}
    return dictInfo

def getInfoFromDRS(dirpath,projectdir,dictInfo):
    '''
    Returns info from project directory and the DRS path to the file
    :param dirpath:
    :param drsstructure:
    :return:
    '''
    #stemdir = getStem(dirpath, projectdir)
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
    return filexra
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

