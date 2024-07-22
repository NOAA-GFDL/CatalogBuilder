#!/usr/bin/env python

import os
from intakebuilder import localcrawler, CSVwriter
import logging
logger = logging.getLogger('local')
hdlr = logging.FileHandler('/nbhome/a1r/logs/local.log')
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def main():
    #######INPUT HERE OR USE FROM A CONFIG FILE LATER######
#   project_dir = "/Users/ar46/data_cmip6/CMIP6/"  # DRS COMPLIANT PROJECT DIR
    project_dir = "/uda/CMIP6/"#
    #CMIP/NOAA-GFDL/GFDL-ESM4/"
    csvfile = "/nbhome/a1r/intakebuilder_cats/intake_local.csv" ##"/Users/ar46/PycharmProjects/CatalogBuilder/intakebuilder/test/intake_local.csv"
    #######################################################
    ######### SEARCH FILTERS ###########################
    dictFilter = {}
    dictFilter["source_prefix"]= 'CMIP6/' #CMIP/CMCC/CMCC-CM2-SR5' #'CMIP6/CMIP/' #NOAA-GFDL/GFDL-CM4/' #/CMIP/NOAA-GFDL/GFDL-ESM4/' #Must specify something here, at least the project level
   #COMMENT  dictFilter["miptable"] = "Amon" #Remove this if you don't want to filter by miptable
   #COMMENT dictFilter["varname"] = "tas"   #Remove this if you don't want to filter by variable name
    #########################################################
    dictInfo = {}
    project_dir = project_dir.rstrip("/")
    logger.info("Calling localcrawler.crawlLocal") 
    print("Calling localcrawler.crawlLocal")
    list_files = localcrawler.crawlLocal(project_dir, dictFilter, logger)
    headers = CSVwriter.getHeader()
    if (not os.path.exists(csvfile)):
        os.makedirs(os.path.dirname(csvfile), exist_ok=True)
    CSVwriter.listdict_to_csv(list_files, headers, csvfile)
    print("CSV generated at:", os.path.abspath(csvfile))
    logger.info("CSV generated at"+ os.path.abspath(csvfile))
if __name__ == '__main__':
    main()
