fitting_function
~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   fitting_function = lorentz

**Meaning**
   Selects the spectral peak line shape. ``lorentz`` uses a Lorentzian with
   fitted HWHM. ``dho`` uses the velocity-spectrum damped harmonic oscillator
   and reports half of its FWHM as the equivalent HWHM. ``auto`` fits both
   candidates and compares AICc, preferring Lorentz in the weak-damping limit
   where ``hwhm / center < 0.05``.

**Default**
   ``lorentz`` for backward-compatible line-shape interpretation.

**DHO diagnostics**
   DHO fits are classified as underdamped, critical, or overdamped in
   ``<out_files_name>_LORENTZ-<q-index>.models``. Overdamped DHO fits are
   omitted from the ordinary phonon-lifetime table; the model file reports
   their slow and fast relaxation times instead. The same file includes peak
   significance and unresolved-width or width-bound flags.

**Related parameters**

- :doc:`fit_peak_strategy <fit_peak_strategy>`
- :doc:`fit_baseline_model <fit_baseline_model>`
- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
