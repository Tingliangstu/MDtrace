Installation
============

MDtrace 1.0 requires Python 3.10 or newer.

From source
-----------

.. code-block:: bash

   git clone https://github.com/Tingliangstu/MDtrace.git mdtrace
   cd mdtrace
   python -m pip install .
   mdtrace -h

The required NumPy, SciPy, netCDF4, Matplotlib, and Seaborn dependencies are
installed automatically.

Optional CuPy backend
---------------------

Install exactly one CuPy wheel matching the CUDA major version available on
the machine:

.. code-block:: bash

   # Choose one; do not install both.
   python -m pip install cupy-cuda12x
   python -m pip install cupy-cuda13x

Alternatively:

.. code-block:: bash

   conda install -c conda-forge cupy

Enable the GPU SED kernel with

.. code-block:: text

   backend = cupy

The current implementation uses one GPU per MDtrace process. CuPy accelerates
SED computation; plotting and spectral fitting remain CPU operations.
