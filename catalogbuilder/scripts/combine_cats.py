import pandas as pd
import json
import pathlib
import sys 
import os
#Set the csv files to be combined. The csv files here are the catalog files. 

#csv1 = "/home/a1r/github/noaa-gfdl/catalogs/CM4.5v01_om5b06_piC_noBLING.csv"
json1 = "/home/a1r/github/noaa-gfdl/catalogs/CM4.5v01_om5b06_piC_noBLING.json" 

#Assume csv is in the same path and deduce the filename

p1 = pathlib.PurePath(json1)
csv1 =  p1.with_suffix('.csv')
print(csv1)

json2 = "/home/a1r/github/noaa-gfdl/catalogs/ESM4.5v01_om5b04_piC.json"
p2 = pathlib.Path(json2)
csv2 = p2.with_suffix('.csv')
print(csv2)


cat_csvs = [csv1,csv2] #TODO check for valid paths, pass it with cmd line if necessary 

#####Check if the header of the csvs are the same #######


#### If the headers are the same, append the data frames together and create the combined csv 
combined_json = "/home/a1r/github/noaa-gfdl/catalogs/combined_CM4.5v01_om5b06_piC_noBLING_and_ESM4.5v01_om5b04_piC.json"
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
