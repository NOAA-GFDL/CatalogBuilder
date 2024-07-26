import os
#from intakebuilder import getinfo, builderconfig
from . import getinfo, builderconfig
import sys
import re
import operator as op
'''
localcrawler crawls through the local file path, then calls helper functions in the package to getinfo.
It finally returns a list of dict. eg {'project': 'CMIP6', 'path': '/uda/CMIP6/CDRMIP/NCC/NorESM2-LM/esm-pi-cdr-pulse/r1i1p1f1/Emon/zg/gn/v20191108/zg_Emon_NorESM2-LM_esm-pi-cdr-pulse_r1i1p1f1_gn_192001-192912.nc', 'variable': 'zg', 'mip_table': 'Emon', 'model': 'NorESM2-LM', 'experiment_id': 'esm-pi-cdr-pulse', 'ensemble_member': 'r1i1p1f1', 'grid_label': 'gn', 'temporal subset': '192001-192912', 'institute': 'NCC', 'version': 'v20191108'}
'''
def crawlLocal(projectdir, dictFilter,dictFilterIgnore,logger,configyaml,slow):
    '''
    crawl through the local directory and run through the getInfo.. functions
    :param projectdir:
    :return:listfiles which has a dictionary of all key/value pairs for each file to be added to the csv
    '''
    listfiles = []
    pat = None
    if("realm" in dictFilter.keys()) & (("frequency") in dictFilter.keys()):
        pat = re.compile('({}/{}/{}/{})'.format(dictFilter["realm"],"ts",dictFilter["frequency"],dictFilter["chunk_freq"]))
    
    orig_pat = pat

    if configyaml:
       headerlist = configyaml.headerlist
    else:
       headerlist = builderconfig.headerlist

    #For those columns that we cannot find in output path template or output file template from config yaml, we have hooks
    #now to look up the netcdf dataset if slow option is True
    #todo catch exceptions upon furhter testing
    list_ptemplate = configyaml.output_path_template
    list_ftemplate = configyaml.output_file_template
    set_ptemplate = set(list_ptemplate)
    set_ftemplate = set(list_ftemplate)
    #print(headerlist)
    #print(list_ptemplate)
    #print(list_ftemplate)
    diffcols  = [x for x in headerlist  if x not in set_ptemplate]
    missingcols = [col for col in diffcols if col not in set_ftemplate]
    missingcols.remove("path") #because we get this anyway
    print("Missing cols from metadata sources:", missingcols)

   
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
               # remove those keys that are not CSV headers 
               # move it so its one time 
               rmkeys = []
               for dkeys in dictInfo.keys():
                  if dkeys not in headerlist:
                      rmkeys.append(dkeys) 
               rmkeys = list(set(rmkeys))
               for k in rmkeys: dictInfo.pop(k,None)
               if (bool(dictInfo)) & ("standard_name" in missingcols) & (slow == False):
               #If we badly need standard name, we use gfdl cmip mapping tables especially when one does not prefer the slow option. Useful for MDTF runs
                   cfname = getinfo.getStandardName(dictInfo["variable_id"])
                   dictInfo["standard_name"] = cfname
                   print("standard name from look-up table-", cfname)
               # todo do the reverse if slow is on. Open file no matter what and populate dictionary values and if there is something missed out
               # we can scan filenames or config etc 
               #here, we will see if there are missing header values and compare with file attributes if slow option is turned on
               if (slow == True) & (bool(dictInfo) == True) :
                    print("Slow option turned on.. lets open some files using xarray and lookup atts",filename)
                    #todo we could look at var attributes, but right now we stick to those that are necessary. scope to extend this easily to missngcols or if header info is not in config yaml 
                    if "standard_name" in missingcols: 
                        dictInfo["standard_name"] = "na"
                        getinfo.getInfoFromVarAtts(dictInfo["path"],dictInfo["variable_id"],dictInfo)
 
               listfiles.append(dictInfo)

    return listfiles
