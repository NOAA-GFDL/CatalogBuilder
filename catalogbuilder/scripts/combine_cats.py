import pandas as pd
import json
from jsondiff import diff
import pathlib
import sys 
import os
#Get the catalog files to be combined. 

#USER INPUT BEGINS 

#Pass the json catalog spec AND the combined_json which is the output path

json1 = "/home/a1r/github/noaa-gfdl/catalogs/CM4.5v01_om5b06_piC_noBLING.json" 
json2 = "/home/a1r/github/noaa-gfdl/catalogs/ESM4.5v01_om5b04_piC.json"
combined_json = "/home/a1r/github/noaa-gfdl/catalogs/combined_CM4.5v01_om5b06_piC_noBLING_and_ESM4.5v01_om5b04_piC.json"

#USER INPUT ENDS

#Assume csv is in the same path and deduce the filename

p1 = pathlib.PurePath(json1)
csv1 =  p1.with_suffix('.csv')
print(csv1)

p2 = pathlib.Path(json2)
csv2 = p2.with_suffix('.csv')
print(csv2)


cat_csvs = [csv1,csv2] #TODO check for valid paths, pass it with cmd line if necessary 

#####Check if the schema is the same
with open(json1) as f1, open(json2) as f2:
    json_obj1 = json.load(f1)
    json_obj2 = json.load(f2) 
differ = diff(json_obj1, json_obj2) 
print("INFO: Schema differs")
print(differ)
if len(differ.keys()) == 1:
  if "catalog_file" in differ.keys():
      print("We can combine since the catalog_file is the only difference")
else:
  print("Schema likely varies significantly, cannot combine")
  sys.exit()
#### If the headers are the same, append the data frames together and create the combined csv 
p3 = pathlib.Path(combined_json)
combined_csv = p3.with_suffix('.csv')

df_concat = pd.concat([pd.read_csv(f) for f in cat_csvs], ignore_index = True)
#df_concat = pd.concat([pd.read_csv(f) for f in cat_csvs])
df_concat = df_concat.drop(['Unnamed: 0'],axis=1)
df_concat.to_csv(combined_csv, index=False)

#Write out a catalog specification 
f = open(json1)
catspec = json.load(f)
for catalog_file in catspec['catalog_file']:
   catspec['catalog_file'] = os.fspath(combined_csv)
#Write out the combined json 
 
json_data = json.dumps(catspec,indent=4)
with open(combined_json,'w') as outfile:
  outfile.write(json_data)


#Print pointers 

print("Combined catalog specification- ", combined_json)
print("Combined csv/catalog- ", combined_csv)
