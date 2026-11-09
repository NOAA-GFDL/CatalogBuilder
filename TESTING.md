# Testing CatalogBuilder
This guide explains how to run the CatalogBuilder test suite locally, what each test covers, and how the tests are run in CI.
## Prerequisites
Set up a development environment as described in the [developer documentation](doc/developers.rst), then install the package and the extra test dependency from the root of the repository:
```bash
pip install -e .
pip install netcdf4
```
`pytest` is installed automatically as a dependency of the package.
> **Note:** Run all commands below from the **root of the repository**. Several tests use relative paths (e.g. `archive/...`) and write output files to the current working directory.
## Quick start
```bash
# 1. Create the sample (empty) netCDF files under ./archive
python catalogbuilder/scripts/make_sample_data.py
# 2. Generate a catalog from the test config (used by the CI-only test below)
python catalogbuilder/scripts/gen_intake_gfdl.py --config catalogbuilder/tests/test_config.yaml
# 3. Run the test suite
pytest -v catalogbuilder
```
A successful run ends with something like:
```
15 passed, 1 xfailed
```
The single `xfailed` test is expected locally; see [CI-only test](#ci-only-test-test_ci_dynamicpy).
### Running a subset of tests
```bash
# A single file
pytest -v catalogbuilder/tests/test_import.py
# A single test
pytest -v catalogbuilder/tests/test_create_catalog.py::test_create_catalog_fill
# Tests matching a keyword
pytest -v catalogbuilder -k slow_mode
```
## Test layout
Tests live in [`catalogbuilder/tests/`](catalogbuilder/tests). The default test path is set in [`catalogbuilder/pytest.ini`](catalogbuilder/pytest.ini).
| File | What it tests |
|------|---------------|
| `test_import.py` | The `catalogbuilder` package and `intakebuilder` modules import correctly. |
| `test_ingestion.py` | A json/csv pair can be opened by intake_esm |
| `test_create_catalog.py` | End-to-end catalog generation from sample data, both from a config file and from the default config (`configs/config_default.yaml`), and the `--fill` / `--no-fill` behavior for missing values. |
| `test_slow_mode_offline_lookup.py` | Slow mode falls back to the offline `standard_name` lookup when reading file attributes fails (uses `unittest.mock`). |
| `test_determine_bump.py` | `.github/scripts/determine_bump.py`, which reads the version-bump checkbox from PR descriptions. |
| `test_ci_dynamic.py` | Opens a catalog generated during the CI run (see below). Marked `xfail`. |
Supporting config files:
- `test_config.yaml` — config used to generate `catalogbuilder/cats/gfdl_autotest_from_yaml.{csv,json}`.
- `fill-test-config.yaml` — config with an extra `test_empty` column, used to exercise `--fill` / `--no-fill`.
### Sample data
`catalogbuilder/scripts/make_sample_data.py` creates empty netCDF files under `./archive/am5/...` that mimic a GFDL post-processing directory tree. Tests that build catalogs call `make_sample_data()` themselves, so you only need to run the script manually before step 2 of the quick start or when running the CLI by hand.
### CI-only test (`test_ci_dynamic.py`)
This test reads `workflow-artifacts1/gfdl_autotest_from_yaml.json`, which CI produces by uploading and re-downloading the catalog generated from `test_config.yaml`. It is marked `@pytest.mark.xfail`, so it shows as `xfailed` locally. CI runs pytest with `--runxfail` to make it a real test.
To reproduce the CI behavior locally:
```bash
mkdir -p workflow-artifacts1
cp catalogbuilder/cats/gfdl_autotest_from_yaml.{csv,json} workflow-artifacts1/
pytest -v --runxfail catalogbuilder
```
## Catalog validation (compval)
CI also validates the generated catalogs with the comprehensive validator:
```bash
python catalogbuilder/scripts/gen_intake_gfdl.py \
  archive/am5/am5/am5f3b1r0/c96L65_am5f3b1r0_pdclim1850F/gfdl.ncrc5-deploy-prod-openmp/pp gfdl_autotest
python catalogbuilder/scripts/compval.py --proper_generation -tf gfdl_autotest.json catalogbuilder/cats/gfdl_template.json
python catalogbuilder/scripts/compval.py --proper_generation -tf catalogbuilder/cats/gfdl_autotest_from_yaml.json
```
The `-tf` (`--test-failure`) flag prints errors instead of raising. Because the sample data does not populate every required column, errors such as `'member_id' contains empty values` are expected and the command still exits successfully. See `python catalogbuilder/scripts/compval.py --help` and [`doc/validation.rst`](doc/validation.rst) for details.
## Continuous integration
These GitHub Actions workflows run on pull requests:
| Workflow | What it does |
|----------|--------------|
| [`test-pip-install-run-pytest.yml`](.github/workflows/test-pip-install-run-pytest.yml) | Installs with pip, runs `codespell` on `doc/` and `pylint` (non-blocking), generates sample data and catalogs, runs `pytest -v --runxfail catalogbuilder`, and runs `compval`. |
| [`build-conda.yml`](.github/workflows/build-conda.yml) | Builds the conda package with `conda build .`, which also runs the import tests in `meta.yaml`. (PRs to `main` and version tags.) |
| [`conda-pkg-extra-tests.yml`](.github/workflows/conda-pkg-extra-tests.yml) | Builds the conda package, installs it into a clean environment, and runs `test_create_catalog.py` with that environment's `pytest`. (PRs to `main` only.) See [Conda package build](#conda-package-build). |
| [`validate-pr.yml`](.github/workflows/validate-pr.yml) | Checks that exactly one version-bump checkbox is ticked in the PR description. |
`publish-conda.yml` also builds the package, but it runs on pushes to `main` and uploads to the `noaa-gfdl` Anaconda channel. It is a release step, not a test.
To run the same lint checks locally:
```bash
pip install codespell pylint
codespell --ignore-words-list="nd,te" --skip="doc/_build/*" doc/
pylint catalogbuilder --exit-zero
```
## Conda package build
The conda recipe is [`meta.yaml`](meta.yaml). The conda package is tested at two levels:
1. **Recipe tests (during `conda build`)** — the `test: imports:` section of `meta.yaml` checks that these modules import from the built package:
   - `catalogbuilder`
   - `catalogbuilder.cats`
   - `catalogbuilder.scripts`
   - `catalogbuilder.scripts.gen_intake_gfdl`
   If any import fails, `conda build` fails. When you add a new subpackage or a module that must ship with the package, consider adding it here.
2. **Extra tests (`conda-pkg-extra-tests.yml`)** — after building, CI installs the local build into a fresh environment and runs `test_create_catalog.py` with that environment's `pytest`. This catches missing runtime dependencies in `meta.yaml`. The generated `sample-mdtf-catalog.{csv,json}` and `default-mdtf-catalog.{csv,json}` are uploaded as workflow artifacts.
   > **Note:** Because `catalogbuilder/` and `catalogbuilder/tests/` both contain `__init__.py`, pytest's default import mode puts the repository root on `sys.path`. The test code is therefore likely imported from the checked-out source rather than the installed package. The runtime dependencies still come from the conda environment.
To reproduce the CI steps locally (requires `conda`; CI uses the `continuumio/miniconda3` image):
```bash
conda config --append channels conda-forge
conda config --append channels noaa-gfdl
conda install -y conda-build conda-verify
conda build .
conda create -y -n catalogbuildertest
conda install -y -n catalogbuildertest catalogbuilder --use-local
conda run -n catalogbuildertest pytest catalogbuilder/tests/test_create_catalog.py
```
When you add a runtime dependency, update `meta.yaml` (`requirements: run:`), `pyproject.toml`, and `environment.yml` together, or the conda build and tests may fail even though the pip-based workflow passes.
## Cleaning up
Tests and scripts write catalogs (`*.csv`, `*.json`) to the repository root and sample data to `archive/`. These are ignored by `.gitignore`, but `workflow-artifacts1/` and `catalogbuilder/cats/gfdl_autotest_from_yaml.{csv,json}` are not, so take care not to commit them. To remove all generated files:
```bash
rm -rf archive/ workflow-artifacts1/ ./*.csv ./*.json
rm -f catalogbuilder/cats/gfdl_autotest_from_yaml.{csv,json}
```
## Adding tests
- Add new test files to `catalogbuilder/tests/` with a `test_` prefix so pytest discovers them.
- If a test needs input data, call `make_sample_data.make_sample_data()` rather than relying on files that already exist.
- Use a unique `output_path` for generated catalogs so that tests do not overwrite each other's output.
- Mock network or file-system access (e.g. with `unittest.mock.patch`) when behavior depends on data that the sample files cannot provide; see `test_slow_mode_offline_lookup.py` for an example.
- Before opening a pull request, make sure `pytest -v catalogbuilder` passes (or `pytest -v --runxfail catalogbuilder` after following the [CI-only test](#ci-only-test-test_ci_dynamicpy) steps).
