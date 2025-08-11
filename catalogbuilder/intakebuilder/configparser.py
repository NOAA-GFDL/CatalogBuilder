import yaml
import os
class Config:
    def __init__(self, config,logger):
        self.config = config
        with open(self.config, 'r') as file:
            configfile = yaml.safe_load(file)
        try:
            self.input_path = configfile['input_path']
        except:
            self.input_path = None
            logger.debug("input_path does not exist in config")
            pass
        try:
            self.output_path = configfile['output_path']
        except:
            self.output_path = None
            logger.debug("output_path does not exist in config")
            pass 
        try:
            self.headerlist = configfile['headerlist']
            logger.debug("headerlist :"+(str)(self.headerlist))
        except:
            raise KeyError("headerlist does not exist in config")
        try:
            self.input_path_template = configfile['input_path_template']
            logger.debug("input_path_template :"+(str)(self.input_path_template))
        except:
            raise KeyError("input_path_template does not exist in config")
        try:
            self.input_file_template = configfile['input_file_template']
            logger.debug("input_file_template :"+ (str)(self.input_file_template))
        except:
            raise KeyError("input_file_template does not exist in config")
        try:
            self.schema = configfile['schema']
            logger.info("schema:"+ self.schema)
        except:
            self.schema = None
            pass

