import intake_esm, intake, dmget
cat = "/home/a1r/github/noaa-gfdl/catalogs/c96L65_am5f7b10r0_amip30_0806.json"
col = intake.open_esm_datastore(cat)
print("Dataframe summary")
print("---------------------")
print(col.df)
#lets search
freq = "day"
cfname = "air_temperature"
esmcat = col.search(frequency = freq, standard_name = cfname)
print("Search results in:")
print("---------------------")
print(esmcat)
##dmget data
print("dmgetting")
print("---------------------")
dmstatus = esmcat.df["path"].apply(dmget.dmgetmagic)
print("dgmet status")
print("---------------------")
dmstatus = esmcat.df["path"].apply(dmget.dmgetmagic)
print(dmstatus)
print("Aggregating and creating a dictionary with dataset names as keys and the values as the xarray dataset object")
dset_dict = esmcat.to_dataset_dict(cdf_kwargs={'chunks': {'time':5}, 'decode_times': False})
print("print dataset keys/names")
print("---------------------")
for k in dset_dict.keys(): 
    print(k)

