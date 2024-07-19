import os
from intakebuilder import getinfo, builderconfig
import sys
import re
import operator as op
'''
localcrawler crawls through the local file path, then calls helper functions in the package to getinfo.
It finally returns a list of dict. eg {'project': 'CMIP6', 'path': '/uda/CMIP6/CDRMIP/NCC/NorESM2-LM/esm-pi-cdr-pulse/r1i1p1f1/Emon/zg/gn/v20191108/zg_Emon_NorESM2-LM_esm-pi-cdr-pulse_r1i1p1f1_gn_192001-192912.nc', 'variable': 'zg', 'mip_table': 'Emon', 'model': 'NorESM2-LM', 'experiment_id': 'esm-pi-cdr-pulse', 'ensemble_member': 'r1i1p1f1', 'grid_label': 'gn', 'temporal subset': '192001-192912', 'institute': 'NCC', 'version': 'v20191108'}

'''
def crawlLocal(projectdir, dictFilter,dictFilterIgnore,logger,configyaml):
    '''
    Craw through the local directory and run through the getInfo.. functions
    :param projectdir:
    :return:listfiles which has a dictionary of all key/value pairs for each file to be added to the csv
    '''
    listfiles = []
    pat = None
    if("realm" in dictFilter.keys()) & (("frequency") in dictFilter.keys()):
        pat = re.compile('({}/{}/{}/{})'.format(dictFilter["realm"],"ts",dictFilter["frequency"],dictFilter["chunk_freq"]))
    
    orig_pat = pat

    #TODO INCLUDE filter in traversing through directories at the top
    for dirpath, dirs, files in os.walk(projectdir):
        searchpath = dirpath
        if (orig_pat is None):
            pat = dirpath  #we assume matching entire path
        if(pat is not None):
            m = re.search(pat, searchpath)
            for filename in files:
               # get info from filename
               filepath = os.path.join(dirpath,filename)  # 1 AR: Bugfix: this needs to join dirpath and filename to get the full path to the file

               #if filename.startswith("."):
               #    logger.debug("Skipping hidden file", filepath)
               #    continue
               if not filename.endswith(".nc"):
                   logger.debug("FILE does not end with .nc. Skipping", filepath)
                   continue
               logger.info(dirpath+"/"+filename)
               dictInfo = {}
               dictInfo = getinfo.getProject(projectdir, dictInfo)
               # get info from filename
               #filepath = os.path.join(dirpath,filename)  # 1 AR: Bugfix: this needs to join dirpath and filename to get the full path to the file
               dictInfo["path"]=filepath
               if (op.countOf(filename,".") == 1):
                 dictInfo = getinfo.getInfoFromFilename(filename,dictInfo, logger)
               else:
                 dictInfo = getinfo.getInfoFromGFDLFilename(filename,dictInfo, logger)
               dictInfo = getinfo.getInfoFromGFDLDRS(dirpath, projectdir, dictInfo,configyaml)
               list_bad_modellabel = ["","piControl","land-hist","piClim-SO2","abrupt-4xCO2","hist-piAer","hist-piNTCF","piClim-ghg","piClim-OC","hist-GHG","piClim-BC","1pctCO2"]
               list_bad_chunklabel = ['DO_NOT_USE']
               if "source_id" in dictInfo: 
                   if(dictInfo["source_id"] in list_bad_modellabel):
                       logger.debug("Found experiment name in model column, skipping this possibly bad DRS filename",filepath)
                   #   continue
               if "chunk_freq" in dictInfo:
                   if(dictInfo["chunk_freq"] in list_bad_chunklabel):
                       logger.debug("Found bad chunk, skipping this possibly bad DRS filename",filepath)
                       continue     
 
               if configyaml:
                   headerlist = configyaml.headerlist
               else:
                   headerlist = builderconfig.headerlist
               # remove those keys that are not CSV headers 
               # move it so its one time 
               rmkeys = []
               for dkeys in dictInfo.keys():
                  if dkeys not in headerlist:
                      rmkeys.append(dkeys) 
               rmkeys = list(set(rmkeys))

               for k in rmkeys: dictInfo.pop(k,None)
 
               listfiles.append(dictInfo)
    return listfiles
