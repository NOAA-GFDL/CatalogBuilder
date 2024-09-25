import catalogbuilder
from catalogbuilder.scripts import gen_intake_gfdl
import sys, os 

#This is an example call to run catalog builder using a yaml config file.
package_dir = os.path.dirname(os.path.abspath(__file__))
configyaml = os.path.join(package_dir, 'configs/config-example.yml')
input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"
output_path = "sample-mdtf-catalog"

def create_catalog_from_config(input_path=input_path,output_path=output_path,configyaml=configyaml):
    csv, json = gen_intake_gfdl.create_catalog(input_path=input_path,output_path=output_path,config=configyaml)
    return(csv,json)

if __name__ == '__main__':
    create_catalog_from_config(input_path,output_path,configyaml)
    

