from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from catalogbuilder.scripts import gen_intake_gfdl, gen_intake_gfdl_runner_config, gen_intake_gfdl_runner, make_sample_data
from unittest.mock import patch


def write_mock_zarr_store(path):
    path.mkdir(parents=True)
    (path / ".zgroup").write_text("{}")
    (path / ".zattrs").write_text("{}")


def write_real_zarr_store(path, var="abs550aer", zarr_format=3, consolidated=None):
    ds = xr.Dataset(
        {
            var: (
                ("time", "lat", "lon"),
                np.arange(8, dtype=np.float32).reshape(2, 2, 2),
            )
        },
        coords={
            "time": [0, 1],
            "lat": [0.0, 1.0],
            "lon": [0.0, 1.0],
        },
    )
    ds[var].attrs.update(
        {
            "standard_name": "atmosphere_absorption_optical_thickness_due_to_ambient_aerosol_particles",
            "units": "1",
        }
    )
    ds.to_zarr(path, mode="w", zarr_format=zarr_format, consolidated=consolidated)


def write_cmip_zarr_config(path, include_standard_name=False):
    headerlist = [
        "activity_id",
        "institution_id",
        "source_id",
        "experiment_id",
        "member_id",
        "table_id",
        "variable_id",
        "grid_label",
        "version_id",
        "path",
    ]
    if include_standard_name:
        headerlist.insert(-1, "standard_name")
    path.write_text(
        "\n".join(
            [
                f"headerlist: {headerlist}",
                'input_path_template: ["NA", "activity_id", "institution_id", "source_id", "experiment_id", "member_id", "table_id", "variable_id", "grid_label"]',
                'input_file_template: ["version_id"]',
            ]
        )
    )


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
    write_cmip_zarr_config(configyaml)

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
    write_cmip_zarr_config(configyaml)

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


@pytest.mark.parametrize("zarr_format", [2, 3])
def test_create_catalog_zarr_slow_reads_standard_name(tmp_path, zarr_format):
    input_path = tmp_path / "CMIP6"
    zarr_store = input_path / "AerChemMIP" / "NOAA-GFDL" / "GFDL-ESM4" / "hist-piNTCF" / "r1i1p1f1" / "AERmon" / "abs550aer" / "gr1" / "v20260831.zarr"
    write_real_zarr_store(zarr_store, zarr_format=zarr_format)

    configyaml = tmp_path / "cmip-zarr-config.yaml"
    write_cmip_zarr_config(configyaml, include_standard_name=True)
    output_path = tmp_path / f"zarr-catalog-v{zarr_format}"

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
            slow=True,
            strict=False,
            verbose=False,
            zarr=True,
        )

    df = pd.read_csv(csv_path, keep_default_na=False)
    assert len(df) == 1
    assert df.loc[0, "standard_name"] == "atmosphere_absorption_optical_thickness_due_to_ambient_aerosol_particles"

    with open(json_path) as f:
        catalog_json = json.load(f)
    assert catalog_json["assets"]["format"] == "zarr"


def test_create_catalog_zarr_slow_without_consolidated_metadata(tmp_path):
    input_path = tmp_path / "CMIP6"
    zarr_store = input_path / "AerChemMIP" / "NOAA-GFDL" / "GFDL-ESM4" / "hist-piNTCF" / "r1i1p1f1" / "AERmon" / "abs550aer" / "gr1" / "v20260831.zarr"
    write_real_zarr_store(zarr_store, zarr_format=2, consolidated=False)

    configyaml = tmp_path / "cmip-zarr-config.yaml"
    write_cmip_zarr_config(configyaml, include_standard_name=True)
    output_path = tmp_path / "zarr-catalog-unconsolidated"

    with patch('catalogbuilder.scripts.gen_intake_gfdl.time.sleep', return_value=None):
        csv_path, _ = gen_intake_gfdl.create_catalog(
            input_path=str(input_path),
            output_path=str(output_path),
            config=configyaml,
            fill=False,
            filter_realm=None,
            filter_freq=None,
            filter_chunk=None,
            overwrite=True,
            append=False,
            slow=True,
            strict=False,
            verbose=False,
            zarr=True,
        )

    df = pd.read_csv(csv_path, keep_default_na=False)
    assert len(df) == 1
    assert df.loc[0, "standard_name"] == "atmosphere_absorption_optical_thickness_due_to_ambient_aerosol_particles"


def test_create_catalog_zarr_slow_open_failure_falls_back_to_lookup(tmp_path):
    input_path = tmp_path / "CMIP6"
    zarr_store = input_path / "AerChemMIP" / "NOAA-GFDL" / "GFDL-ESM4" / "hist-piNTCF" / "r1i1p1f1" / "AERmon" / "abs550aer" / "gr1" / "v20260831.zarr"
    write_real_zarr_store(zarr_store, zarr_format=3)

    configyaml = tmp_path / "cmip-zarr-config.yaml"
    write_cmip_zarr_config(configyaml, include_standard_name=True)
    output_path = tmp_path / "zarr-catalog-open-failure"

    with patch('catalogbuilder.scripts.gen_intake_gfdl.time.sleep', return_value=None):
        with patch('catalogbuilder.intakebuilder.getinfo.xr.open_zarr', side_effect=OSError("broken zarr")):
            with patch('catalogbuilder.intakebuilder.getinfo.getStandardName', return_value={"abs550aer": "offline_standard_name"}):
                csv_path, _ = gen_intake_gfdl.create_catalog(
                    input_path=str(input_path),
                    output_path=str(output_path),
                    config=configyaml,
                    fill=False,
                    filter_realm=None,
                    filter_freq=None,
                    filter_chunk=None,
                    overwrite=True,
                    append=False,
                    slow=True,
                    strict=False,
                    verbose=False,
                    zarr=True,
                )

    df = pd.read_csv(csv_path, keep_default_na=False)
    assert len(df) == 1
    assert df.loc[0, "standard_name"] == "offline_standard_name"
