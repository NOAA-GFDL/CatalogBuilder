""" 
Defines the subdirectory patterns and filename components used by make_sample_data.py to build
the sample GFDL post-processing directory tree for testing. Each list (realm, freq, vars, time)
provides the set of values used when constructing directory names and filenames under the root
directory defined in make_sample_data.py.
"""

realm = [
'atmos',
'atmos_cmip'
]
freq = [
'monthly',
]
vars = [
'tas',
'uas'
]
time = [
'000101-000112',
'000201-000212'
]
