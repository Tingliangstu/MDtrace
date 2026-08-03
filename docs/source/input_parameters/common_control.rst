Control
-------

These parameters select what MDtrace should do and which implementation it
should use.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 28 18 54

   * - Parameter
     - Default
     - Purpose
   * - :doc:`action <action>`
     - ``thinking``
     - Select automatic workflow, forced computation, plotting, or fitting.
   * - :doc:`method <method>`
     - ``sed``
     - Select the reciprocal-space observable; 1.1.0 supports SED.
   * - :doc:`backend <backend>`
     - ``numpy``
     - Select NumPy CPU computation or optional CuPy GPU computation.

Minimal control block:

.. code-block:: text

   action  = thinking
   method  = sed
   backend = numpy

:doc:`Back to Common parameters <common>`

.. toctree::
   :hidden:

   action
   method
   backend
