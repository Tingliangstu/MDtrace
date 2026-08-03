Output and display
==================

These parameters set the main output prefix and whether saved figures are also
shown in an interactive window.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 28 18 54

   * - Parameter
     - Default
     - Purpose
   * - :doc:`out_files_name <out_files_name>`
     - ``mdtrace``
     - Set the prefix and optional relative path for main outputs.
   * - :doc:`if_show_figures <if_show_figures>`
     - ``0``
     - Save without blocking at ``0``; also show interactively at ``1``.

.. code-block:: text

   out_files_name   = SrTiO3
   if_show_figures  = 0

See :doc:`../sed_workflow/output_files` for the complete SED output layout.

:doc:`Back to Common parameters <common>`

.. toctree::
   :hidden:

   out_files_name
   if_show_figures
