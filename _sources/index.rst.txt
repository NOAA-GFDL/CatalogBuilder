.. Catalog Builder documentation master file, created by
   sphinx-quickstart on Wed Feb 14 00:31:23 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Catalog Builder's documentation!
===========================================


The Catalog Builder API will collect building blocks necessary to build a data catalog which can then be ingested in climate analysis scripts/workflow, leveraging the use of intake-esm and xarray.

Tested on posix file system, S3 and GFDL post-processed (select simulations, components) at this time. This repository has unit tests (pytest) and incorporated the same in GitHub Actions, when a PR is open or a push is initiated.

See our `Github repository <https://github.com/aradhakrishnanGFDL/CatalogBuilder>`_ here.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   background
   generation
   usage
   presentation 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
