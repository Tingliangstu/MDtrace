Spectral peak fitting
=====================

These parameters control peak detection, local fit ranges, Lorentz/DHO model
selection, and per-Q or combined lifetime output.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 33 17 50

   * - Parameter
     - Default
     - Purpose
   * - :doc:`lorentz_fit_all_qpoint <lorentz_fit_all_qpoint>`
     - ``0``
     - Fit every Q point or only ``qpoint_slice_index``.
   * - :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
     - ``None``
     - Set the lowest frequency used for detection and fitting.
   * - :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
     - ``None``
     - Set the highest frequency used for detection and fitting.
   * - :doc:`fitting_function <fitting_function>`
     - ``auto``
     - Select Lorentz, velocity-DHO, or AICc-based automatic selection.
   * - :doc:`peak_min_significance <peak_min_significance>`
     - ``4.0``
     - Set the dimensionless local robust detection threshold.
   * - :doc:`initial_guess_hwhm <initial_guess_hwhm>`
     - ``0.001``
     - Set the optimizer's initial HWHM in THz.
   * - :doc:`peak_max_hwhm <peak_max_hwhm>`
     - ``1e6``
     - Bound the fitted HWHM in THz.
   * - :doc:`modulate_factor <modulate_factor>`
     - ``0``
     - Remove samples from both ends of each local fit range.
   * - :doc:`re_output_total_freq_lifetime <re_output_total_freq_lifetime>`
     - ``0``
     - Rebuild combined results after replacing one Q-point fit.

Recommended single-Q tuning block:

.. code-block:: text

   action                           = fit
   qpoint_slice_index               = 23
   lorentz_fit_all_qpoint           = 0
   lorentz_fit_freq_min             = 0
   lorentz_fit_freq_max             = 25
   peak_min_significance            = 5.0
   fitting_function                 = auto
   initial_guess_hwhm               = 0.01
   re_output_total_freq_lifetime    = 0

Inspect several single-Q figures before setting
``lorentz_fit_all_qpoint = 1``. See :doc:`../peak_detection` for the complete
detection and line-shape workflow and :doc:`../theory` for the reported
lifetime convention.

:doc:`Back to SED parameters <sed>`

.. toctree::
   :hidden:

   lorentz_fit_all_qpoint
   lorentz_fit_freq_min
   lorentz_fit_freq_max
   fitting_function
   peak_min_significance
   initial_guess_hwhm
   peak_max_hwhm
   modulate_factor
   re_output_total_freq_lifetime
