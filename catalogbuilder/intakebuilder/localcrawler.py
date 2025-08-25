'''
localcrawler crawls through the local file path, then calls helper functions in the package to getinfo.
It finally returns a list of dict
'''

import os
from . import getinfo
import re
import logger
logger = logging.getLogger(

def crawlLocal(projectdir, dictFilter):
    '''
    Craw through the local directory and run through the getInfo.. functions
    :param projectdir:
    :return:listfiles which has a dictionary of all key/value pairs for each file to be added to the csv
    '''
    listfiles = []
    pat = None
    if "miptable" in dictFilter.keys()) and "varname" in dictFilter.keys():
        pat = re.compile('({}/{}/)'.format(dictFilter["miptable"],dictFilter["varname"]))
    elif "miptable" in dictFilter.keys():
        pat = re.compile('({}/)'.format(dictFilter["miptable"]))
    elif "varname" in dictFilter.keys():
        pat = re.compile('({}/)'.format(dictFilter["varname"]))
    orig_pat = pat

    #TODO INCLUDE filter in traversing through directories at the top
    for dirpath, dirs, files in os.walk(projectdir):

        if dictFilter["source_prefix"] in dirpath: #TODO improved filtering
            searchpath = dirpath

            if not orig_pat:
                pat = dirpath  #we assume matching entire path

            if pat:
                m = re.search(pat, searchpath)

                for filename in files:
                   logger.info(dirpath+"/"+filename)
                   dictInfo = {}
                   dictInfo = getinfo.getProject(projectdir, dictInfo)

                   # get info from filename
                   filepath = os.path.join(dirpath,filename)  # 1 AR: Bugfix: this needs to join dirpath and filename to get the full path to the file

                   if not filename.endswith(".nc"):
                        logger.debug("FILE does not end with .nc. Skipping", filepath)
                        continue

                   dictInfo["path"]=filepath
                   dictInfo = getinfo.getInfoFromFilename(filename, dictInfo)
                   dictInfo = getinfo.getInfoFromDRS(dirpath, projectdir, dictInfo)

                   #eliminate bad DRS filenames spotted
                   list_bad_modellabel = ["","piControl","land-hist","piClim-SO2","abrupt-4xCO2","hist-piAer","hist-piNTCF","piClim-ghg","piClim-OC","hist-GHG","piClim-BC","1pctCO2"]

                   if dictInfo["model"] in list_bad_modellabel:
                      logger.debug("Found experiment name in model column, skipping this possibly bad DRS filename", dictInfo["experiment"],filepath)
                      continue
                   listfiles.append(dictInfo)
    return listfiles
