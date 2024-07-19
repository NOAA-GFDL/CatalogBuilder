import re
import boto3
import botocore
from intakebuilder import getinfo

'''
s3 crawler crawls through the S3 bucket, passes the bucket path to the helper functions to getinfo.
Finally it returns a list of dictionaries. 
'''
def sss_crawler(projectdir,dictFilter,project_root, logger):
    region = 'us-west-2'
    s3client = boto3.client('s3', region_name=region,
                            config=botocore.client.Config(signature_version=botocore.UNSIGNED))

    s3prefix = "s3:/"
    filetype = ".nc"
    project_bucket = projectdir.split("/")[2]
    #######################################################
    listfiles = []
    pat = None
    logger.debug(dictFilter.keys())
    if("miptable" in dictFilter.keys()) & (("varname") in dictFilter.keys()):
        pat = re.compile('({}/{}/)'.format(dictFilter["miptable"],dictFilter["varname"]))
    elif("miptable" in dictFilter.keys()):
        pat = re.compile('({}/)'.format(dictFilter["miptable"]))
    elif(("varname") in dictFilter.keys()):
        pat = re.compile('({}/)'.format(dictFilter["varname"]))
    orig_pat = pat
    paginator = s3client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=project_bucket, Prefix=dictFilter["source_prefix"], Delimiter=filetype):
        for prefixes in result.get('CommonPrefixes'):
            dictInfo = {}
            dictInfo = getinfo.getProject(project_root, dictInfo)
            commonprefix = prefixes.get('Prefix')
            searchpath = commonprefix
            if (orig_pat is None):
                pat = commonprefix #we assume matching entire path
            #filepath = '{}/{}/{}'.format(s3prefix,project_bucket,commonprefix)
          #  print("Search filters applied", dictFilter["source_prefix"], "and", pat)
            if(pat is not None):
                m = re.search(pat, searchpath)
                if m is not None:
                        #print(commonprefix)
                        #print('{}/{}/{}'.format(s3prefix,project_bucket,commonprefix))
                        filepath = '{}/{}/{}'.format(s3prefix,project_bucket,commonprefix)
                        #TODO if filepath already exists in csv we skip
                        dictInfo["path"]=filepath
                        logger.debug(filepath)
                        filename = filepath.split("/")[-1]
                        dirpath = "/".join(filepath.split("/")[0:-1])
                        #projectdird passed to sss_crawler should be s3://bucket/project
                        dictInfo = getinfo.getInfoFromFilename(filename, dictInfo,logger)
                        dictInfo = getinfo.getInfoFromDRS(dirpath, projectdir, dictInfo)
                        #Using YAML instead of this to get frequency and modeling_realm  dictInfo = getinfo.getInfoFromGlobalAtts(filepath, dictInfo)
                        #TODO YAML for all mip_tables
                        dictInfo = getinfo.getinfoFromYAML(dictInfo,"table.yaml",miptable=dictInfo["mip_table"])
                        listfiles.append(dictInfo)
                        logger.debug(dictInfo)
    return listfiles
