#!/usr/bin/env python

import json
import sys
import pandas as pd
import time
import click
import os
from pathlib import Path
import logging
from importlib.resources import files as _files #Using files causes bug..
from catalogbuilder.scripts.compval import compval as cv
from catalogbuilder.intakebuilder import gfdlcrawler, CSVwriter, configparser, getinfo


logger = logging.getLogger(__name__)


def create_catalog(input_path, output_path, config, fill, filter_realm, filter_freq, filter_chunk, overwrite, append, slow, strict, verbose):
    """Generate an intake-ESM-compatible data catalog (CSV + JSON) from a local directory tree.

    Crawls *input_path* for NetCDF files, assembles catalog rows according to the
    supplied (or default) YAML configuration, writes a CSV catalog file and a
    matching intake-ESM JSON descriptor to *output_path*.

    Args:
        input_path (str | None): Root directory to crawl for dataset files.
            May be ``None`` if the value is provided in *config*.
        output_path (str | None): Destination path **without** a file extension.
            The function appends ``.csv`` / ``.json`` automatically.
            May be ``None`` if the value is provided in *config*.
        config (str | os.PathLike | None): Path to a custom YAML configuration
            file.  When ``None`` the package-bundled default config is used.
        fill (bool): When ``True`` (the default), all empty cells in the
            generated CSV are replaced with the string ``'NA'``.  Pass
            ``False`` to leave empty cells as-is.
        filter_realm (str | None): If provided, only files whose
            ``modeling_realm`` matches this value are included.
        filter_freq (str | None): If provided, only files whose ``frequency``
            matches this value are included.
        filter_chunk (str | None): If provided, only files whose
            ``chunk_freq`` matches this value are included.
        overwrite (bool): When ``True``, an existing CSV at *output_path* is
            overwritten rather than raising an error.
        append (bool): When ``True``, new rows are appended to an existing CSV
            (without re-writing the header row).
        slow (bool): When ``True``, ``standard_name`` (or ``long_name``) is
            read directly from each NetCDF file's metadata instead of being
            looked up in an offline table.
        strict (bool): When ``True``, the finished catalog is validated against
            the CV vocabulary embedded in the JSON schema; generation fails if
            any violations are found.
        verbose (bool): When ``True``, log level is set to ``DEBUG``; otherwise
            ``INFO`` is used.

    Returns:
        tuple[str, str]: A 2-tuple ``(csv_path, json_path)`` with the absolute
        paths to the generated catalog files.

    Raises:
        FileNotFoundError: If *input_path* does not exist or the default config
            cannot be located.
        TypeError: If *input_path* or *output_path* cannot be determined from
            the arguments and the config file.
        ValueError: If the parent directory of *output_path* does not exist.
    """

    if not logging.root.handlers:
        log_format = '%(levelname)s:%(funcName)s: %(message)s'
        logging.basicConfig(
            level=logging.DEBUG if verbose else logging.INFO,
            stream=sys.stdout,
            format=log_format
        )

    logger.warning("!!!!! IMPORTANT: RECENT CHANGES TO THE CATALOG BUILDER MAY AFFECT EXISTING WORKFLOWS !!!!!")
    time.sleep(10)

    # Setting up logger
    # Standard mode's level is set as INFO
    # Verbose mode's level is set as DEBUG
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.info("Verbose log activated.\n")
 
    else:
        logger.info("[Mostly] silent log activated\n")

    if strict:
        logger.warning("!!!!! STRICT MODE IS ACTIVE. CATALOG GENERATION WILL FAIL IF ERRORS ARE FOUND !!!!!\n")
        time.sleep(10)

    if config:
        configyaml = configparser.Config(config)
        if input_path is None:
            input_path = configyaml.input_path
        if output_path is None:
            output_path = configyaml.output_path
    else:
            # If user does not pass a config, we will use the default config with the same format to avoid special cases
        try:
            config = _files('catalogbuilder').joinpath('intakebuilder/config_default.yaml')
        except:
            raise FileNotFoundError("Can't locate or read default config, try --config ")
        configyaml = configparser.Config(config)

        if input_path is None:
            input_path = configyaml.input_path
        if output_path is None:
            output_path = configyaml.output_path
    if input_path is None or output_path is None:
        logger.error("Missing: input_path or output_path. Pass it in the config yaml or as command-line option")
        raise TypeError("Missing: input_path or output_path. Pass it in the config yaml or as command-line option")

    if config is None or not configyaml.schema:
        logger.info("Default schema: catalogbuilder/cats/gfdl_template.json")
        template_path = _files('catalogbuilder').joinpath('cats/gfdl_template.json')
    else:
        template_path = configyaml.schema
        logger.info("Using schema from config file", template_path)

    if not os.path.exists(input_path):
        logger.error("Input path does not exist. Adjust configuration.")
        raise FileNotFoundError("Input path does not exist. Adjust configuration.")
    if not os.path.exists(Path(output_path).parent.absolute()):
        logger.error("Output path parent directory does not exist. Adjust configuration.")
        raise ValueError("Output path parent directory does not exist. Adjust configuration.")

    logger.info("input path: "+ input_path)
    logger.info("output path: "+ output_path)
    project_dir = input_path
    csv_path = "{0}.csv".format(output_path)
    json_path = "{0}.json".format(output_path)

    ######### SEARCH FILTERS ###########################

    dictFilter = {}
    dictFilterIgnore = {}
    if filter_realm:
        dictFilter["modeling_realm"] = filter_realm
    if filter_freq:
        dictFilter["frequency"] = filter_freq
    if filter_chunk:
        dictFilter["chunk_freq"] = filter_chunk

    ''' Override config file if necessary for dev
    project_dir = "/archive/oar.gfdl.cmip6/ESM4/DECK/ESM4_1pctCO2_D1/gfdl.ncrc4-intel16-prod-openmp/pp/"
    #for dev csvfile =  "/nbhome/$USER/intakebuilder_cats/intake_gfdl2.csv" 
    dictFilterIgnore = {}
    dictFilter["modeling_realm"]= 'atmos_cmip'
    dictFilter["frequency"] = "monthly"
    dictFilter["chunk_freq"] = "5yr"
    dictFilterIgnore["remove"]= 'DO_NOT_USE'
    '''
    dictInfo = {}
    project_dir = project_dir.rstrip("/")
    logger.debug("Calling gfdlcrawler.crawlLocal")
    list_files = gfdlcrawler.crawlLocal(project_dir, dictFilter, dictFilterIgnore, configyaml,slow)
    #Grabbing data from template JSON, changing CSV path to match output path, and dumping data in new JSON
    with open(template_path, "r") as jsonTemplate:
        data = json.load(jsonTemplate)
        data["catalog_file"] = os.path.abspath(csv_path)
    jsonFile = open(json_path, "w")
    json.dump(data, jsonFile, indent=2)
    jsonFile.close()
    headers = CSVwriter.getHeader(configyaml)

    # When we pass relative path or just the filename the following still needs to not choke
    # so we check if it's a directory first
    if os.path.isdir(os.path.dirname(csv_path)):
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    CSVwriter.listdict_to_csv(list_files, headers, csv_path, overwrite, append,slow)
    df = None

    if not slow and 'standard_name' in headers:
        #If we badly need standard name, we use gfdl cmip mapping tables especially when one does not prefer the slow option. Useful for MDTF runs
        logger.info("Because standard_name is in headerlist and slow mode is off, standard_name will be retrieved from an offline lookup table")
        df = pd.read_csv(os.path.abspath(csv_path), sep=",", header=0,index_col=False)
        df['standard_name'] = df['standard_name'].astype(object)
        list_variable_id = []
        try:
            list_variable_id = df["variable_id"].unique().tolist()
        except:
            raise KeyError("Having trouble finding 'variable_id'... Be sure to add it to the input_path_template field of your configuration")
        dictVarCF = getinfo.getStandardName(list_variable_id)
        for k, v in dictVarCF.items():
            if k is not None:
                mask = df['variable_id'] == k
                df.loc[mask, 'standard_name'] = v

    if fill:
        # Replace NaN values and blank/whitespace-only strings with 'NA' so that
        # the output CSV has no truly empty cells
        if df is None:
            df = pd.read_csv(os.path.abspath(csv_path), sep=",", header=0, index_col=False)
        filled_count = 0
        for column in df.columns:
            had_missing = df[column].isna().any() or df[column].astype(str).str.match(r'^\s*$').any()
            df[column] = df[column].fillna('NA')
            df[column] = df[column].replace(r'^\s*$', 'NA', regex=True)
            if had_missing:
                filled_count += 1
        logger.info(f"Filled empty values in {filled_count} column(s) with 'NA'")

    if df is not None and len(df) != 0:
        df.to_csv(csv_path, index=False)

    # Strict Mode
    if strict:
        vocab = True
        proper_generation = False
        test_failure = False

        #Validate
        cv(json_path,'',vocab, proper_generation, test_failure)

    logger.info("JSON generated at: " + os.path.abspath(json_path))
    logger.info("CSV generated at: " + os.path.abspath(csv_path))
    return(csv_path,json_path)

#Setting up argument parsing/flags
@click.command()
#TODO arguments dont have help message. So consider changing arguments to options?
@click.argument('input_path',required=False,nargs=1)
#,help='The directory path with the datasets to be cataloged. E.g a GFDL PP path till /pp')
@click.argument('output_path',required=False,nargs=1)
#,help='Specify output filename suffix only. e.g. catalog')
@click.option('--config',required=False,type=click.Path(exists=True),nargs=1,help='Path to your yaml config, Use the config_template in intakebuilder repo')
@click.option('--fill/--no-fill', default=True, help="Fill all empty CSV column values with 'NA'. Enabled by default. Use --no-fill to disable.")
@click.option('--filter_realm', nargs=1)
@click.option('--filter_freq', nargs=1)
@click.option('--filter_chunk', nargs=1)
@click.option('--overwrite', is_flag=True, default=False, help='Overwrite existing catalog CSV file')
@click.option('--append', is_flag=True, default=False, help='Append to existing catalog CSV file (without headers)')
@click.option('--slow','-s', is_flag=True, default=False, help='This option looks up standard names in netcdf file to fill up the standard name column if its present in the header specs. If standard_name isnt in your header specs, you dont need this option')
@click.option('--strict', is_flag=True, default=False, help='Strict catalog generation ensures catalogs are compliant with CV standards (as defined in vocabulary section of catalog schema)')
@click.option('--verbose/--silent','-v', default=False, is_flag=True, help='Enables detailed logging') #default has silent option. Use --verbose for detailed logging

def create_catalog_cli(**kwargs):
    return create_catalog(**kwargs)

if __name__ == '__main__':
    create_catalog_cli()
