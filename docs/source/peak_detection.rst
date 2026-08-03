Peak detection and line-shape fitting
=====================================

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

Local fit range
---------------

Each accepted peak is fitted **separately**. MDtrace finds the lowest point of
the seven-bin smoothed log spectrum between the peak and each neighboring
detected peak. Those two valleys define the local fit range. For the first and
last detected peaks, the search extends to the selected frequency boundary.

Only the boundaries come from the smoothed log spectrum. The nonlinear fit
uses every original, unsmoothed, linear-SED sample inside that range. The
default fit has zero added background and is not a simultaneous multi-peak
deconvolution. Consequently, a shoulder or strongly overlapping peak may not
represent an isolated phonon mode even when the numerical fit converges.

The green or grey model curve in a fit figure is drawn only over the local fit
range. Its analytic half-maximum points can lie outside that displayed
segment. In this case MDtrace marks the peak as incomplete and reports a
model-extrapolated HWHM; the corresponding lifetime is qualitative.

Line-shape models
-----------------

``fitting_function = lorentz`` uses the zero-background Lorentzian

.. math::

   \Phi_L(f)
   =
   \frac{A}
   {1+\left[(f-f_0)/h\right]^2},

where :math:`f_0` is the fitted peak frequency, :math:`A` is the peak height,
and :math:`h` is the HWHM.

``fitting_function = dho`` uses the velocity-spectrum damped harmonic
oscillator (DHO)

.. math::

   \Phi_\mathrm{DHO}(f)
   =
   \frac{A\,(2h)^2 f^2}
   {(f^2-f_0^2)^2+(2h)^2 f^2}.

This is the velocity-spectrum form appropriate to the kinetic-energy-weighted
SED calculated by MDtrace. The parameter :math:`h` is half the damping
linewidth in ordinary-frequency units and approaches the peak HWHM in the
weak-damping limit. MDtrace converts it with the same reported convention,
:math:`\tau_\mathrm{SED}=1/(2\pi h)`. For an overdamped DHO, that value is a
linewidth-derived relaxation timescale rather than a strict phonon lifetime.

Automatic model selection
-------------------------

With the default ``fitting_function = auto``, MDtrace fits Lorentz and DHO to
the same data points with the same three fitted parameters. It compares their
small-sample Akaike information criterion (AICc), which balances residual
error against model complexity. The model with lower AICc is preferred, with
two safeguards:

* if the candidates differ by no more than two AICc units, Lorentz is chosen;
* if the fitted DHO has :math:`h/f_0 < 0.05`, its weak-damping line shape is
  effectively Lorentzian, so Lorentz is chosen for the simpler interpretation.

If only one candidate fit succeeds, the successful model is retained. A DHO
is therefore not selected merely because a peak is broad; it must describe
the same local spectrum materially better than Lorentz.

Interpreting difficult peaks
----------------------------

Automatic fitting is a screening tool, not proof that every detected feature
is an independent quasiparticle. Inspect the per-Q fit figures before using
the combined lifetime data quantitatively. Treat incomplete, strongly
overlapping, asymmetric, or overdamped peaks as qualitative. Longer
trajectories improve frequency resolution; mode-projected SED can later help
separate branches that overlap in the total spectrum.

For exact syntax and defaults, open :doc:`input_parameters/sed_fitting`. For
the lifetime convention and derivation, see :doc:`theory`.

:doc:`Back to SED workflow <sed_workflow/index>`
