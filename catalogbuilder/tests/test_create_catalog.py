def test_create_catalog():
      from pathlib import Path
      import catalogbuilder
      from catalogbuilder.scripts import gen_intake_gfdl_runner_config,gen_intake_gfdl_runner
      from catalogbuilder.tests import make_sample_data
      make_sample_data.make_sample_data()
      json, csv = gen_intake_gfdl_runner_config.create_catalog_from_config()
      #to output success/failure in pytest run with conda pkg local install in extra-tests CI workflow#
      print(csv)
      csvpath = Path(csv)
      jsonpath = Path(json)
      assert csvpath.is_file()
      assert jsonpath.is_file()
      #test to run without config so we can test the default configs/config_default.yaml
      json, csv = gen_intake_gfdl_runner.create_catalog_default()
      #to output success/failure in pytest run with conda pkg local install in extra-tests CI workflow#
      print(csv)
      csvpath2 = Path(csv)
      jsonpath2 = Path(json)
      assert csvpath2.is_file()
      assert jsonpath2.is_file()

