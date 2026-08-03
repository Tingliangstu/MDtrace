SED output and plotting
=======================

These parameters control total and partial SED output, dispersion appearance,
and individual-Q spectra.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 29 17 54

   * - Parameter
     - Default
     - Purpose
   * - :doc:`output_partial <output_partial>`
     - ``0``
     - Save element- and direction-resolved SED during computation.
   * - :doc:`plot_partial_SED <plot_partial_SED>`
     - disabled
     - Select an element and optional x/y/z component for later plotting.
   * - :doc:`plot_cutoff_freq <plot_cutoff_freq>`
     - ``None``
     - Set the highest displayed frequency in THz.
   * - :doc:`plot_interval <plot_interval>`
     - ``5.0``
     - Set the frequency tick interval in THz.
   * - :doc:`plot_color <plot_color>`
     - ``RdBu_r``
     - Select the Matplotlib colormap.
   * - :doc:`colorbar_min <colorbar_min>`
     - ``None``
     - Set an optional lower logarithmic color limit.
   * - :doc:`colorbar_max <colorbar_max>`
     - ``None``
     - Set an optional upper logarithmic color limit.
   * - :doc:`use_contourf <use_contourf>`
     - ``0``
     - Use filled contours instead of the default heatmap rendering.
   * - :doc:`plot_slice <plot_slice>`
     - ``0``
     - Plot one Q-point spectrum on a logarithmic intensity axis.
   * - :doc:`qpoint_slice_index <qpoint_slice_index>`
     - ``0``
     - Select the zero-based Q point for a slice or single-Q fit.

Typical plotting block:

.. code-block:: text

   plot_cutoff_freq   = 25
   plot_interval      = 5
   plot_slice         = 1
   qpoint_slice_index = 23
   if_show_figures    = 0

To inspect oxygen motion separately, first compute with
``output_partial = 1`` and later select ``plot_partial_SED = O`` or
``plot_partial_SED = O y``. See :doc:`../sed_workflow/partial_sed` and
:doc:`../sed_workflow/output_files`.

:doc:`Back to SED parameters <sed>`

.. toctree::
   :hidden:

   output_partial
   plot_partial_SED
   plot_cutoff_freq
   plot_interval
   plot_color
   colorbar_min
   colorbar_max
   use_contourf
   plot_slice
   qpoint_slice_index
