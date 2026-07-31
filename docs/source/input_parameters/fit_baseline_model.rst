fit_baseline_model
~~~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   fit_baseline_model = auto

**Meaning**
   Selects the local background used when fitting SED peaks. Accepted values
   are ``none``, ``constant``,
   ``linear``, and ``auto``.

   ``none`` fixes the background to zero. ``constant`` fits one non-negative
   background height per peak cluster. ``linear`` fits non-negative values at
   the left and right edges and interpolates between them. ``auto`` compares
   all three candidates with AICc and prefers the simpler model when their
   AICc values differ by no more than two.

**Default**
   ``auto``.

**Output**
   The selected model, fit interval, center background, slope, AICc, and RSS
   are written to ``<out_files_name>_LORENTZ-<q-index>.baseline``.

**Related parameters**

- :doc:`fit_peak_strategy <fit_peak_strategy>`
- :doc:`fitting_function <fitting_function>`
- :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
- :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
- :doc:`modulate_factor <modulate_factor>`
- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
