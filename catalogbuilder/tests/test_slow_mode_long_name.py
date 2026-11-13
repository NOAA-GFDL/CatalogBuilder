from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
from catalogbuilder.scripts import gen_intake_gfdl
from unittest.mock import patch

PP_SUBDIRS = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"


def write_long_name_only_dataset(tmp_path):
    """
    Write a sample PP tree holding one netCDF file whose variable carries a
    long_name but no standard_name, and return the pp directory to crawl.
    """
    ppdir = tmp_path / PP_SUBDIRS
    tsdir = ppdir / "atmos" / "ts" / "monthly" / "1yr"
    tsdir.mkdir(parents=True, exist_ok=True)
    ds = xr.Dataset(
        {"tas": (("time",), np.zeros(2, dtype="float32"), {"long_name": "Near Surface Air Temperature"})},
        coords={"time": np.arange(2, dtype="float64")},
    )
    ds.to_netcdf(tsdir / "atmos.000101-000112.tas.nc")
    ds.close()
    return ppdir


def test_slow_mode_falls_back_to_long_name(tmp_path):
    """
    Test that slow mode falls back to long_name when a variable carries no
    standard_name attribute.

    The offline lookup is mocked to return nothing so that the netCDF
    attributes are the only source of a standard_name, which is the condition
    the long_name fallback exists for.
    """
    ppdir = write_long_name_only_dataset(tmp_path)
    configyaml = Path(__file__).parent / "test_config.yaml"

    with patch('catalogbuilder.scripts.gen_intake_gfdl.time.sleep', return_value=None):
        with patch('catalogbuilder.intakebuilder.getinfo.getStandardName', return_value={}):
            csv_slow, _ = gen_intake_gfdl.create_catalog(
                input_path=str(ppdir),
                output_path=str(tmp_path / "test-slow-long-name"),
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
            )

    df_slow = pd.read_csv(csv_slow, keep_default_na=False)
    tas_rows = df_slow[df_slow['variable_id'] == 'tas']
    assert len(tas_rows) == 1, "Expected one catalog row for 'tas'"
    assert (tas_rows['standard_name'] == 'Near_Surface_Air_Temperature').all(), \
        "Expected slow mode to fall back to long_name when standard_name is absent"
