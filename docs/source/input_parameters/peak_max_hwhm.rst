peak_max_hwhm
~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   peak_max_hwhm = 0.1

**Meaning**
   User-specified hard maximum for the fitted equivalent HWHM. MDtrace also
   applies a tighter adaptive bound based on the detected peak width,
   frequency-bin spacing, and the local peak window. This prevents a peak
   component from becoming nearly constant and impersonating the baseline.

**Default**
   ``1e6``.

**Notes**
   In most cases, this parameter does not need to be adjusted because the
   adaptive bound is active. Fits that reach it are flagged in the ``.models``
   diagnostic file.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
- :doc:`peak_height <peak_height>`
- :doc:`peak_prominence <peak_prominence>`
- :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
- :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
- :doc:`modulate_factor <modulate_factor>`
