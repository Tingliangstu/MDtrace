peak_height
~~~~~~~~~~~

**Syntax**

.. code-block:: text

   peak_height = 1.0e-3

**Meaning**
   Minimum SED intensity required for mdtrace to treat a point in a q-slice as a
   real peak. It is the basic intensity cutoff for automatic Lorentzian peak
   fitting. Its unit is ``eV/THz``.

**Default**
   ``None`` (disabled).

**Notes**
   Without ``peak_min_significance``, this value is passed to SciPy during the
   original peak-detection path. When ``peak_min_significance`` is enabled,
   ``peak_height`` remains an optional additional filter on the original
   linear SED after adaptive candidate detection.

   Set this parameter from a single-q-point slice first. Use
   ``plot_slice = 1`` and inspect both the plotted spectrum and the frequencies
   printed by mdtrace. If ``peak_height`` is too high, weak but real branches are
   missed. If it is too low, random noise and small shoulders may be fitted as
   artificial phonon modes.

   For noisy spectra, tune ``peak_height`` together with
   ``peak_prominence`` or use ``peak_min_significance`` for a threshold that
   adapts to the local noise. Height controls the absolute intensity threshold,
   while prominence controls how clearly a peak stands out from its local
   background.
   The example value is illustrative; determine a suitable value from the
   plotted single-Q spectrum rather than reusing a threshold from another
   material.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`peak_prominence <peak_prominence>`
- :doc:`peak_min_significance <peak_min_significance>`
- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
- :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
- :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
- :doc:`modulate_factor <modulate_factor>`
