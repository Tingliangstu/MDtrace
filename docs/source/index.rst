MDtrace documentation
=====================

**MDtrace** traces reciprocal-space physics in molecular-dynamics
trajectories. Version 1.1.0 provides a production workflow for calculating,
plotting, decomposing, and fitting phonon spectral energy density (SED).

New users should begin with :doc:`starting`. To look up an input keyword,
open :doc:`input_parameters`; every supported parameter is listed in a
clickable index and has its own reference page. Method concepts, files,
units, fitting conventions, and implementation details are organized under
the :doc:`sed_workflow/index` chapter.

Choose a starting point
-----------------------

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 28 72

   * - Goal
     - Start here
   * - Install MDtrace and run a first calculation
     - :doc:`Quick start <starting>`
   * - Find the syntax or default for one keyword
     - :doc:`Input parameters <input_parameters>`
   * - Understand the complete SED calculation and fitting workflow
     - :doc:`SED workflow <sed_workflow/index>`
   * - Diagnose an input, trajectory, fitting, or output problem
     - :doc:`Troubleshooting <troubleshooting>`

.. toctree::
   :maxdepth: 2
   :caption: Getting started

   introduction
   installation
   starting

.. toctree::
   :maxdepth: 4
   :caption: Input parameters

   input_parameters

.. toctree::
   :maxdepth: 2
   :caption: SED workflow

   sed_workflow/index

.. toctree::
   :maxdepth: 2
   :caption: Help and reference

   troubleshooting
   release_notes
   reference
   publications
