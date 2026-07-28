Combining Catalogs
==================

Users are able to merge two catalogs into a single catalog specification by using the catalog combing tool. The tool can be accessed by calling the ``combine_cats.py`` script located in the catalogbuilder/scripts directory.


It is intended for users who seek to:

* Concatenate two CSVs into one combined CSV.
* Produce a new JSON catalog specification that points to the combined CSV.

Using the catalog combining tool
--------------------------------

The catalog combining tool can be found in catalogbuilder/scripts/combine_cats.py

It can be called like this:

    combine_catalogs.py -i jsoncatalog -i jsoncatalog2 -o outputjson

Example usage: combine_cats.py -i /home/a1r/github/noaa-gfdl/catalogs/CM4.5v01_om5b06_piC_noBLING.json -i /home/a1r/github/noaa-gfdl/catalogs/ESM4.5v01_om5b04_piC.json -o combinedcat.json

Options:
  -i, --inputfiles TEXT   Pass json catalog files to-be-combined, space
                          separated  [required]
  -o, --output_path TEXT  Specify the output json path  [required]
  --help                  Show this message and exit.

