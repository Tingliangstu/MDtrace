Installation
============

From source
-----------

.. code-block:: bash

   git clone https://github.com/Tingliangstu/mdtrace.git
   cd mdtrace
   python -m pip install .
   mdtrace -h

The required NumPy, SciPy, netCDF4, Matplotlib, and plotting dependencies are
installed automatically.

Optional CuPy backend
---------------------

Install the CuPy wheel matching the installed CUDA Toolkit:

.. code-block:: bash

   # Choose one
   python -m pip install cupy-cuda12x
   python -m pip install cupy-cuda13x

Alternatively:

.. code-block:: bash

   conda install -c conda-forge cupy

Enable the GPU SED kernel with

.. code-block:: text

   backend = cupy

The current implementation uses one GPU per MDtrace process.
