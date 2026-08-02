Automatic SED peak detection
============================

MDtrace finds spectral peaks automatically with one user control:

.. code-block:: text

   peak_min_significance = 4.0

This is a dimensionless **local prominence-to-noise threshold**. It is not an
absolute SED intensity cutoff, so the same value can detect a weak peak on a
low background and a strong peak on a high background. The default ``4.0`` is
a practical starting point for most spectra.

Detection at a glance
---------------------

The automatic detector follows six steps:

.. code-block:: text

   original linear SED
          │
          ▼
   natural log + 7-bin Hann smoothing
          │
          ├── locate candidate peaks and their prominence
          │
          ▼
   residual = raw log SED - smoothed log SED
          │
          ▼
   local noise = 31-bin rolling MAD
          │
          ▼
   significance = prominence / local noise
          │
          ▼
   keep candidates with significance ≥ peak_min_significance
          │
          ▼
   refine and fit using the original, unsmoothed, linear SED

.. figure:: _static/SED-peak-detection-smoothing-q1.svg
   :name: sed-peak-detection-smoothing
   :alt: Raw and Hann-smoothed log SED with the local residual-noise estimate
   :align: center
   :width: 100%

   Automatic peak-detection preprocessing for Q-point #1 of the SrTiO3
   example over 0--5 THz. **a**, The raw log SED and its seven-bin
   Hann-smoothed copy. **b**, Their residual and the local noise band estimated
   with a 31-bin rolling median absolute deviation (MAD). Smoothing is used
   only for detection and local fitting-window boundaries; the fitted
   frequencies and linewidths come from the original SED.

Reading the figure
------------------

Panel **a** shows why MDtrace detects peaks on the logarithmic spectrum. The
logarithm compresses the large SED dynamic range, allowing weak branches to
remain visible beside intense peaks. Multiplying the entire SED by a constant
only shifts this curve vertically, so it does not change the prominence score.

The seven-bin Hann curve suppresses isolated bin-to-bin fluctuations while
preserving the broader peak structure. MDtrace measures candidate prominence
on this blue curve rather than on the jagged grey curve.

Panel **b** shows the residual

.. math::

   r(f)=y_\mathrm{raw}(f)-y_\mathrm{smooth}(f),

where

.. math::

   y_\mathrm{raw}(f)
   =
   \ln\!\left[
   \frac{\Phi(\mathbf q,f)}{1\,\mathrm{eV\,THz^{-1}}}
   \right].

The cyan band is the local robust noise scale. MDtrace evaluates a rolling
31-bin MAD and converts it to a standard-deviation-like quantity:

.. math::

   \sigma_\mathrm{local}(f)
   =
   1.4826\,
   \operatorname{MAD}_{31}[r(f)].

A small global noise floor is also applied so that an unusually smooth region
cannot produce an artificially infinite significance.

Accepting a candidate
---------------------

For every candidate on the smoothed log spectrum, MDtrace calculates

.. math::

   S(f_\mathrm{peak})
   =
   \frac{P_\mathrm{log}(f_\mathrm{peak})}
        {\sigma_\mathrm{local}(f_\mathrm{peak})},

where :math:`P_\mathrm{log}` is the peak prominence relative to its surrounding
valleys. The candidate is retained when

.. math::

   S(f_\mathrm{peak})
   \ge
   \mathtt{peak\_min\_significance}.

Thus, ``peak_min_significance = 4.0`` requires the local prominence to be at
least four times the robust local-noise estimate. This is not a formal
four-sigma probability because neighboring FFT bins and smoothed samples are
correlated.

After acceptance, MDtrace searches within three bins of the candidate and
moves it to the maximum of the **original linear SED**. The original values are
then used for the Lorentz or DHO fit; the blue smoothed curve is never used to
calculate HWHM or lifetime.

Choosing ``peak_min_significance``
----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 34 22 44

   * - What you see
     - Suggested change
     - Expected effect
   * - Stable peaks are detected correctly
     - Keep ``4.0``
     - Retains the default balance between weak peaks and noise
   * - A reproducible weak peak is missing
     - Lower gradually, for example ``4.0`` to ``3.5``
     - Accepts lower-significance candidates; inspect the fit figure carefully
   * - Many noise fluctuations are treated as peaks
     - Raise to ``5.0`` or ``6.0``
     - Keeps fewer, cleaner candidates
   * - One Q-point needs different detection
     - Fit that Q-point separately
     - Avoids changing every Q-point to accommodate one difficult spectrum

For a single-Q check, use:

.. code-block:: text

   action                         = fit
   qpoint_slice_index             = 1
   lorentz_fit_all_qpoint         = 0
   peak_min_significance          = 4.0
   fitting_function               = auto
   re_output_total_freq_lifetime  = 1

Inspect ``Fitting-Qpoint/Fitting-1-qpoint.png`` after each adjustment. Once the
representative Q-points look reasonable, set ``lorentz_fit_all_qpoint = 1``.

What this parameter does not control
------------------------------------

``peak_min_significance`` decides whether a candidate exists. It does not
choose Lorentz versus DHO, improve the frequency resolution, or make an
overlapping/asymmetric peak into an isolated mode. Use ``fitting_function`` for
the line shape and interpret strongly overlapping or incomplete peaks
qualitatively.

For the exact input syntax and all fitting parameters, see
:doc:`input_parameters`. For the lifetime definition and fitting assumptions,
see :doc:`theory`.
