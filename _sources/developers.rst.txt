==============
For developers
==============

The Catalog Builder team welcomes all contributions. If you would like to help develop the package, please follow the steps outlined below.


How to contribute
=================

Set up a clean environment
--------------------------

First, create a new environment for your Catalog Builder development work. The recommended approach is to use a `python virtual environment (venv) <https://docs.python.org/3/library/venv.html>`_. A conda environment will also work fine if such is desired.

.. code-block:: console

   python3 -m venv /path/to/new/virtual/environment

Then, activate the environment by sourcing the activation script. The command varies by operating system and shell:

* **Linux/macOS (bash/zsh):**

.. code-block:: console

   source /path/to/new/virtual/environment/bin/activate

* **Linux/macOS (csh):**

.. code-block:: console

   source /path/to/new/virtual/environment/bin/activate.csh

* **Linux/macOS (fish):**

.. code-block:: console

   source /path/to/new/virtual/environment/bin/activate.fish

* **Linux/macOS (pwsh):**

.. code-block:: console

   /path/to/new/virtual/environment/bin/activate.ps1

* **Windows (Command Prompt):**

.. code-block:: console

   \path\to\new\virtual\environment\Scripts\activate.bat

* **Windows (PowerShell):**

.. code-block:: console

   \path\to\new\virtual\environment\Scripts\Activate.ps1

Clone the Catalog Builder source code
-------------------------------------

Clone the `Github repository <https://github.com/NOAA-GFDL/CatalogBuilder>`_ using ssh:

.. code-block:: console

   git clone git@github.com:NOAA-GFDL/CatalogBuilder.git

or https:

.. code-block:: console

   git clone https://github.com/NOAA-GFDL/CatalogBuilder.git

Install the package
-------------------

It is recommended that developers install an `editable <https://setuptools.pypa.io/en/latest/userguide/development_mode.html>`_ Catalog Builder package. This makes development simple as any local changes will immediately be testable. From the root of the repository, run:

.. code-block:: console

   pip install -e .

.. note::
Sometimes it is necessary to deactivate and reactivate the virtual environment in order for PATH to be properly resolved.
