@pytest.mark.skip
def test_create_catalog():
      import catalogbuilder
      from catalogbuilder.scripts import gen_intake_gfdl_runner_config
      import make_sample_data
      make_sample_data.make_sample_data()
      json, csv = gen_intake_gfdl_runner_config.create_catalog_from_config()
      #to output success/failure in pytest run with conda pkg local install in extra-tests CI workflow#
      csv = "/home/runner/work/forkCatalogBuilder-/sample-mdtf-catalog.csv"
      json = "/home/runner/work/forkCatalogBuilder-/sample-mdtf-catalog.json"
      csvpath = Path(csv)
      jsonpath = Path(json)
      assert csvpath.is_file()
      assert jsonpath.is_file()
  

