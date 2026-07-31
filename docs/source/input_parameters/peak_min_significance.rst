peak_min_significance
~~~~~~~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   peak_min_significance = 4.0

**Meaning**
   Minimum dimensionless local-noise significance used for adaptive SED peak
   detection. A value of ``4.0`` requires a candidate's prominence on the
   Hann-smoothed log SED to be at least four times the local robust noise
   estimate.

**Default**
   ``None`` (adaptive detection disabled for backward compatibility).

**Definition**
   The complete workflow is:

   .. code-block:: text

      original linear SED
          |
          v
      natural logarithm
          |
          v
      7-point Hann smoothing for detection only
          |
          v
      original log SED - smoothed log SED
          |
          v
      31-point rolling MAD local-noise estimate
          |
          v
      smoothed-log prominence / local noise
          |
          v
      retain candidates above peak_min_significance
          |
          v
      refine positions and fit the original unsmoothed SED

   For peak detection, MDtrace forms the natural-log spectrum, smooths a copy
   with a seven-point Hann window, and computes the residual

   .. math::

      r(f)=y_\mathrm{raw}(f)-y_\mathrm{smooth}(f).

   Noise is estimated within a 31-sample window using

   .. math::

      \sigma_\mathrm{local}(f)
      =
      1.4826\,
      \operatorname{median}_\mathrm{window}
      \left|
      r-\operatorname{median}_\mathrm{window}(r)
      \right|.

   A candidate is accepted when its smoothed-log prominence divided by
   :math:`\sigma_\mathrm{local}` is no smaller than
   ``peak_min_significance``. This makes the parameter a dimensionless local
   robust signal-to-noise threshold rather than an absolute SED intensity
   threshold.

**Notes**
   The value is a robust, local signal-to-noise score, not a formal
   four-sigma probability. A larger value rejects more weak or noisy
   candidates; a smaller value detects more peaks.

   Smoothing is used only to identify candidates. The detected frequency is
   refined to a nearby maximum of the original SED, and Lorentzian fitting
   uses the original, unsmoothed, linear SED.

   ``peak_height`` and ``peak_prominence`` remain optional additional absolute
   filters in ``eV/THz``. Leave them as ``None`` to test the adaptive
   significance criterion by itself.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`peak_height <peak_height>`
- :doc:`peak_prominence <peak_prominence>`
- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
- :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
- :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
