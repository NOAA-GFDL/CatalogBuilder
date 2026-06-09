from pathlib import Path
import pandas as pd
from catalogbuilder.scripts import gen_intake_gfdl, make_sample_data
from unittest.mock import patch
import pytest


def test_slow_mode_offline_lookup_fallback():
    """
    Test that slow mode uses offline lookup for entries where file retrieval failed.

    NOTE: This test mocks getinfo.getStandardName() because we cannot guarantee
    the test data will have entries with 'na' standard_name values (where file
    retrieval failed). The mock allows us to test the slow mode fallback logic
    deterministically without relying on specific test data characteristics.

    We also mock getInfoFromVarAtts to simulate file retrieval failure (leaving
    standard_name as 'na'), which is the condition that triggers the fallback.
    """
    make_sample_data.make_sample_data()
    configyaml = Path(__file__).parent / "test_config.yaml"
    input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"

    # Mock the offline lookup to return predictable results
    mock_lookup_dict = {
        'tas': 'air_temperature',
        'uas': 'eastward_wind',
    }

    # Mock getInfoFromVarAtts to simulate file retrieval failure (leaves standard_name as 'na')
    def mock_get_info(path, var_id, dictInfo):
        # Do nothing - leave standard_name as 'na' to simulate failure
        pass

    with patch('catalogbuilder.intakebuilder.getinfo.getInfoFromVarAtts', side_effect=mock_get_info):
        with patch('catalogbuilder.intakebuilder.getinfo.getStandardName', return_value=mock_lookup_dict) as mock_get:
            # Generate catalog with slow mode enabled
            csv_slow, _ = gen_intake_gfdl.create_catalog(
                input_path=input_path,
                output_path="test-slow-offline-lookup",
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

            # Verify the offline lookup was called (the fallback path was hit)
            mock_get.assert_called_once()

    # Read the generated CSV
    df_slow = pd.read_csv(csv_slow, keep_default_na=False)

    # Verify standard_name column exists
    assert 'standard_name' in df_slow.columns, "standard_name column missing from CSV"

    # Verify the dataframe was written to CSV successfully
    assert len(df_slow) > 0, "CSV should contain at least one row"

    # Verify that the offline lookup populated standard_name values
    # Since mock_get_info leaves standard_name as 'na' and our lookup provides
    # mappings for 'tas' and 'uas', those entries should be updated
    tas_rows = df_slow[df_slow['variable_id'] == 'tas']
    if len(tas_rows) > 0:
        assert (tas_rows['standard_name'] == 'air_temperature').all(), \
            "Expected offline lookup to populate standard_name for 'tas'"

    uas_rows = df_slow[df_slow['variable_id'] == 'uas']
    if len(uas_rows) > 0:
        assert (uas_rows['standard_name'] == 'eastward_wind').all(), \
            "Expected offline lookup to populate standard_name for 'uas'"


def test_slow_mode_offline_lookup_failure():
    """
    Test that when offline lookup raises an exception in slow mode,
    the exception is logged and re-raised.
    """
    make_sample_data.make_sample_data()
    configyaml = Path(__file__).parent / "test_config.yaml"
    input_path = "archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp"

    # Mock getInfoFromVarAtts to simulate file retrieval failure
    def mock_get_info(path, var_id, dictInfo):
        pass

    with patch('catalogbuilder.intakebuilder.getinfo.getInfoFromVarAtts', side_effect=mock_get_info):
        with patch('catalogbuilder.intakebuilder.getinfo.getStandardName', side_effect=Exception("Lookup failed")):
            with pytest.raises(Exception, match="Lookup failed"):
                gen_intake_gfdl.create_catalog(
                    input_path=input_path,
                    output_path="test-slow-offline-lookup-fail",
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
