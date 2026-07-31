peak_prominence
~~~~~~~~~~~~~~~

**Syntax**

.. code-block:: text

   peak_prominence = 1.0e-4

**Meaning**
   Minimum amount by which a peak must stand out from its surrounding
   background before mdtrace fits it. Use this to avoid fitting small noise
   features as phonon peaks. Its unit is ``eV/THz``.

**Default**
   ``None`` (disabled).

**Notes**
   Prominence measures how strongly a peak stands above the surrounding
   baseline. In practical SED fitting, this parameter is often more important
   than ``peak_height`` because SED intensity can vary strongly from one branch
   or q-point to another.

   A high ``peak_prominence`` keeps only isolated, well-separated peaks. This is
   useful when the spectrum has a noisy baseline, but it can miss weak acoustic
   modes, low-intensity optical modes, or broadened peaks near avoided crossings.
   A low ``peak_prominence`` detects more peaks, but it may also select noise,
   shoulders, or small oscillations around a broad peak.

   This parameter is an absolute threshold in the linear SED unit. When
   ``peak_min_significance`` is enabled, ``peak_prominence`` is retained as an
   optional additional filter after local-noise-adaptive candidate detection.
   It is not the same quantity as the dimensionless log-SED significance.

   Recommended workflow:

   - Set ``plot_slice = 1`` and choose a representative ``qpoint_slice_index``.
   - Start from a conservative ``peak_height`` and ``peak_prominence``.
   - Compare the printed peak frequencies with the visible SED slice.
   - Lower ``peak_prominence`` if real branches are missing.
   - Raise ``peak_prominence`` if noise is being fitted.

   The example value is illustrative. Choose it from the actual single-Q
   spectrum because intensities differ between systems.

   The Lorentzian lifetime extracted by mdtrace depends on the fitted HWHM
   :math:`\gamma`. If the wrong peaks are detected here, the later lifetime
   output will also be wrong.

:doc:`Back to Parameter Index <../input_parameters>`

Related parameters
------------------

- :doc:`peak_height <peak_height>`
- :doc:`peak_min_significance <peak_min_significance>`
- :doc:`initial_guess_hwhm <initial_guess_hwhm>`
- :doc:`peak_max_hwhm <peak_max_hwhm>`
- :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
- :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
- :doc:`modulate_factor <modulate_factor>`
