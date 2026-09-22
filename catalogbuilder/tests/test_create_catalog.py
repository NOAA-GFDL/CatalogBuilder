from pathlib import Path
import json
import pandas as pd
from catalogbuilder.scripts import gen_intake_gfdl, gen_intake_gfdl_runner_config, gen_intake_gfdl_runner, make_sample_data
from unittest.mock import patch


def write_mock_zarr_store(path):
    path.mkdir(parents=True)
    (path / ".zgroup").write_text("{}")
    (path / ".zattrs").write_text("{}")


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
    configyaml = Path(__file__).parent / "fill-test-config.yaml"
    input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"

    # Generate catalog with fill disabled and confirm missing values are present
    csv_nofill, _ = gen_intake_gfdl.create_catalog(
        input_path=input_path, output_path="test-nofill-catalog",
        config=configyaml, fill=False, filter_realm=None, filter_freq=None,
        filter_chunk=None, overwrite=True, append=False, slow=False, strict=False, verbose=False,
    )
    df_nofill = pd.read_csv(csv_nofill, keep_default_na=True)
    assert df_nofill.isna().any().any(), (
        "Expected at least one missing value somewhere in the catalog when fill is disabled (--no-fill)"
    )

    # Generate catalog with fill enabled and confirm all missing values are replaced
    csv_fill, _ = gen_intake_gfdl.create_catalog(
        input_path=input_path, output_path="test-fill-catalog",
        config=configyaml, fill=True, filter_realm=None, filter_freq=None,
        filter_chunk=None, overwrite=True, append=False, slow=False, strict=False, verbose=False,
    )
    df_fill = pd.read_csv(csv_fill, keep_default_na=False)
    assert not df_fill.isna().any().any(), (
        "Expected no NaN values anywhere in the catalog when fill is enabled (--fill)"
    )
    assert not (df_fill == '').any().any(), (
        "Expected no empty strings anywhere in the catalog when fill is enabled (--fill)"
    )
    assert (df_fill == 'NA').any().any(), (
        "Expected at least one value to be filled with 'NA' when fill is enabled (--fill)"
    )


def test_create_catalog_zarr(tmp_path):
    input_path = tmp_path / "CMIP6"
    zarr_store = input_path / "AerChemMIP" / "NOAA-GFDL" / "GFDL-ESM4" / "hist-piNTCF" / "r1i1p1f1" / "AERmon" / "abs550aer" / "gr1" / "v20260831.zarr"
    write_mock_zarr_store(zarr_store)
    configyaml = tmp_path / "cmip-zarr-config.yaml"
    configyaml.write_text(
        "\n".join(
            [
                'headerlist: ["activity_id", "institution_id", "source_id", "experiment_id", "member_id", "table_id", "variable_id", "grid_label", "version_id", "path"]',
                'input_path_template: ["NA", "activity_id", "institution_id", "source_id", "experiment_id", "member_id", "table_id", "variable_id", "grid_label", "version_id"]',
                'input_file_template: ["NA"]',
            ]
        )
    )

    output_path = tmp_path / "zarr-catalog"

    with patch('catalogbuilder.scripts.gen_intake_gfdl.time.sleep', return_value=None):
        csv_path, json_path = gen_intake_gfdl.create_catalog(
            input_path=str(input_path),
            output_path=str(output_path),
            config=configyaml,
            fill=False,
            filter_realm=None,
            filter_freq=None,
            filter_chunk=None,
            overwrite=True,
            append=False,
            slow=False,
            strict=False,
            verbose=False,
            zarr=True,
        )

    df = pd.read_csv(csv_path, keep_default_na=False)
    assert len(df) == 1
    assert df.loc[0, "path"].endswith("v20260831.zarr")
    assert df.loc[0, "version_id"] == "v20260831"
    assert df.loc[0, "variable_id"] == "abs550aer"
    assert df.loc[0, "table_id"] == "AERmon"

    with open(json_path) as f:
        catalog_json = json.load(f)
    assert catalog_json["assets"]["format"] == "zarr"


def test_create_catalog_version_named_zarr_store(tmp_path):
    input_path = tmp_path / "CMIP6"
    zarr_store = input_path / "AerChemMIP" / "NOAA-GFDL" / "GFDL-ESM4" / "hist-piNTCF" / "r1i1p1f1" / "AERmon" / "abs550aer" / "gr1" / "v20260831"
    write_mock_zarr_store(zarr_store)

    configyaml = tmp_path / "cmip-zarr-config.yaml"
    configyaml.write_text(
        "\n".join(
            [
                'headerlist: ["activity_id", "institution_id", "source_id", "experiment_id", "member_id", "table_id", "variable_id", "grid_label", "version_id", "path"]',
                'input_path_template: ["NA", "activity_id", "institution_id", "source_id", "experiment_id", "member_id", "table_id", "variable_id", "grid_label", "version_id"]',
                'input_file_template: ["NA"]',
            ]
        )
    )

    output_path = tmp_path / "version-zarr-catalog"

    with patch('catalogbuilder.scripts.gen_intake_gfdl.time.sleep', return_value=None):
        csv_path, json_path = gen_intake_gfdl.create_catalog(
            input_path=str(input_path),
            output_path=str(output_path),
            config=configyaml,
            fill=False,
            filter_realm=None,
            filter_freq=None,
            filter_chunk=None,
            overwrite=True,
            append=False,
            slow=False,
            strict=False,
            verbose=False,
            zarr=True,
        )

    df = pd.read_csv(csv_path, keep_default_na=False)
    assert len(df) == 1
    assert df.loc[0, "path"].endswith("v20260831")
    assert df.loc[0, "version_id"] == "v20260831"
    assert df.loc[0, "variable_id"] == "abs550aer"
    assert df.loc[0, "table_id"] == "AERmon"
    assert df.loc[0, "activity_id"] == "AerChemMIP"

    with open(json_path) as f:
        catalog_json = json.load(f)
    assert catalog_json["assets"]["format"] == "zarr"
