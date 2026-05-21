from pathlib import Path
import pandas as pd
from importlib.resources import files
from catalogbuilder.scripts import gen_intake_gfdl, gen_intake_gfdl_runner_config, gen_intake_gfdl_runner, make_sample_data

def test_create_catalog():
      make_sample_data.make_sample_data()
      csv, json = gen_intake_gfdl_runner_config.create_catalog_from_config()
      #to output success/failure in pytest run with conda pkg local install in extra-tests CI workflow#
      print(csv)
      csvpath = Path(csv)
      jsonpath = Path(json)
      assert csvpath.is_file()
      assert jsonpath.is_file()
      #test to run without config so we can test the default configs/config_default.yaml
      csv, json = gen_intake_gfdl_runner.create_catalog_default()
      #to output success/failure in pytest run with conda pkg local install in extra-tests CI workflow#
      print(csv)
      csvpath2 = Path(csv)
      jsonpath2 = Path(json)
      assert csvpath2.is_file()
      assert jsonpath2.is_file()

def test_create_catalog_fill():
    make_sample_data.make_sample_data()
    configyaml = files('catalogbuilder').joinpath('intakebuilder/config_default.yaml')
    input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"

    # Generate catalog with fill disabled and confirm missing values are present
    csv_nofill, _ = gen_intake_gfdl.create_catalog(
        input_path=input_path, output_path="test-nofill-catalog",
        config=configyaml, fill=False, filter_realm=None, filter_freq=None,
        filter_chunk=None, overwrite=True, append=False, slow=False, strict=False, verbose=False,
    )
    df_nofill = pd.read_csv(csv_nofill, keep_default_na=True)
    assert df_nofill.isna().any().any(), (
        "Expected at least one missing value when fill is disabled (--no-fill)"
    )

    # Generate catalog with fill enabled and confirm no missing values remain
    csv_fill, _ = gen_intake_gfdl.create_catalog(
        input_path=input_path, output_path="test-fill-catalog",
        config=configyaml, fill=True, filter_realm=None, filter_freq=None,
        filter_chunk=None, overwrite=True, append=False, slow=False, strict=False, verbose=False,
    )
    df_fill = pd.read_csv(csv_fill, keep_default_na=False)
    assert not df_fill.isna().any().any(), (
        "Expected no NaN values when fill is enabled (--fill)"
    )
    assert not (df_fill == '').any().any(), (
        "Expected no empty strings when fill is enabled (--fill)"
    )
