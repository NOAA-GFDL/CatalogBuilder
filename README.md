# CatalogBuilder

The GFDL Catalog Builder is a python community package ecosystem” that allows users to generate data catalogs compatible with intake-esm.

Data catalogs simplify data discovery by creating customizable, extendable, and queryable catalogs.

If you would like to use the catalog builder, you must install the [conda package](https://anaconda.org/NOAA-GFDL/catalogbuilder), clone the [github repository](https://github.com/NOAA-GFDL/CatalogBuilder), or use the [FRE command line interface](https://github.com/NOAA-GFDL/fre-cli).


Building a catalog would then look something like this: 

``` 
gen_intake_gfdl.py /archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp $HOME/catalog
```

OR

``` 
fre catalog build --overwrite /archive/path_to_data_dir 
```

If you run into any problems please create an [issue](https://github.com/NOAA-GFDL/CatalogBuilder/issues) here.

Cite our work: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5196586.svg)](https://doi.org/10.5281/zenodo.10787602)

For detailed information regarding the Catalog Builder, see our [project documentation site ](https://noaa-gfdl.github.io/CatalogBuilder/).

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
