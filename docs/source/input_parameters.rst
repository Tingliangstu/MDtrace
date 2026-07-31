Input parameters
================

MDtrace reads a plain-text input file. Each active line has the form

.. code-block:: text

   parameter_name = value

Blank lines and text following ``#`` are ignored. Parameters are divided into a
shared section and method-specific sections so future DSF and EELS options do
not become mixed with SED settings.

Common parameters
-----------------

.. list-table::
   :header-rows: 1
   :widths: 23 18 59

   * - Parameter
     - Default
     - Meaning
   * - ``action``
     - ``thinking``
     - ``thinking`` reuses completed stages; ``compute`` always recalculates;
       ``plot`` and ``fit`` use existing output
   * - ``method``
     - ``sed``
     - ``sed``, preliminary ``dsf``, or reserved ``eels``
   * - ``backend``
     - ``numpy``
     - ``numpy`` or optional ``cupy``
   * - ``trajectory_file``
     - ``dump.xyz``
     - GPUMD XYZ, one LAMMPS dump, or compatible NetCDF
   * - ``out_files_name``
     - ``mdtrace``
     - Output prefix
   * - ``lammps_unit``
     - ``metal``
     - ``metal`` for Angstrom/ps; ``real`` for Angstrom/fs
   * - ``time_step``
     - ``0.0``
     - MD integration step in fs; positive value required for compute
   * - ``output_data_stride``
     - ``0``
     - MD steps between saved frames; positive value required for compute
   * - ``num_blocks``
     - ``5``
     - Trajectory blocks used for spectral averaging
   * - ``max_cores``
     - ``4``
     - Maximum NumPy worker processes; ``1`` is serial
   * - ``prim_unitcell``
     - ``None``
     - Nine row-major primitive-cell values in Angstrom
   * - ``netcdf_compression_level``
     - ``1``
     - zlib compression level for converted text trajectories; ``0`` disables
       compression
   * - ``netcdf_batch_size``
     - ``64``
     - Frames parsed and written per conversion batch

SED structure and sampling
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 23 18 59

   * - Parameter
     - Default
     - Meaning
   * - ``num_atoms``
     - ``0``
     - Number of atoms; positive value required for compute
   * - ``total_num_steps``
     - ``0``
     - Production steps represented by the requested trajectory range
   * - ``basis_lattice_file``
     - ``basis.in``
     - Atom-to-cell, atom-to-basis, and mass mapping
   * - ``supercell_dim``
     - ``1 1 1``
     - Primitive-cell repetitions
   * - ``prim_axis``
     - ``None``
     - Optional nine-value primitive-axis transformation
   * - ``rescale_prim``
     - ``1``
     - Reconstruct the primitive cell from a relaxed trajectory cell

The saved-frame interval is

.. math::

   \Delta t
   =
   \mathtt{time\_step}\,
   \mathtt{output\_data\_stride}.

The requested number of frames is

.. math::

   N_\mathrm{frames}
   =
   \frac{\mathtt{total\_num\_steps}}
   {\mathtt{output\_data\_stride}},

and must be divisible by ``num_blocks``. The input trajectory may contain more
frames; MDtrace reads only the requested range.

SED Q paths
-----------

.. list-table::
   :header-rows: 1
   :widths: 23 18 59

   * - Parameter
     - Default
     - Meaning
   * - ``num_qpaths``
     - ``1``
     - Number of connected path segments
   * - ``q_path_name``
     - ``GA``
     - One label per vertex; ``G`` is displayed as Gamma
   * - ``q_path``
     - ``None``
     - ``num_qpaths + 1`` reduced-coordinate triples

Decimals and fractions are accepted:

.. code-block:: text

   num_qpaths  = 2
   q_path_name = GXM
   q_path      = 0 0 0  1/2 0 0  1/2 1/2 0

Only points commensurate with the finite supercell are retained.

SED plotting and decomposition
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 23 18 59

   * - Parameter
     - Default
     - Meaning
   * - ``plot_cutoff_freq``
     - ``None``
     - Maximum plotted frequency in THz
   * - ``plot_interval``
     - ``5.0``
     - Frequency tick interval in THz
   * - ``plot_color``
     - ``RdBu_r``
     - Matplotlib colormap
   * - ``colorbar_min``, ``colorbar_max``
     - ``None``
     - Optional dimensionless limits for
       ``ln[SED / (1 eV THz^-1)]``
   * - ``use_contourf``
     - ``0``
     - Use filled contours
   * - ``plot_slice``
     - ``0``
     - Plot a single-Q SED in ``eV/THz`` on a logarithmic y-axis
   * - ``qpoint_slice_index``
     - ``0``
     - Zero-based Q-point index
   * - ``if_show_figures``
     - ``0``
     - Show figures interactively
   * - ``output_partial``
     - ``0``
     - Save element and x/y/z components during compute
   * - ``plot_partial_SED``
     - disabled
     - Element plus optional direction, e.g. ``C`` or ``C z``

Partial SED must be enabled during compute:

.. code-block:: text

   output_partial = 1

It can later be selected during plotting:

.. code-block:: text

   plot_partial_SED = C
   # or
   plot_partial_SED = C z

SED spectral-peak fitting
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 27 18 55

   * - Parameter
     - Default
     - Meaning
   * - ``lorentz_fit_all_qpoint``
     - ``0``
     - Fit every Q point
   * - ``lorentz_fit_freq_min``
     - ``None``
     - Lowest fitted frequency in THz
   * - ``lorentz_fit_freq_max``
     - ``None``
     - Highest fitted frequency in THz
   * - ``fit_baseline_model``
     - ``auto``
     - Local baseline: ``none``, ``constant``, ``linear``, or ``auto``
   * - ``fit_peak_strategy``
     - ``auto``
     - Peak grouping: ``independent``, ``joint``, or ``auto``
   * - ``fitting_function``
     - ``lorentz``
     - Line shape: ``lorentz``, ``dho``, or ``auto``
   * - ``peak_height``
     - ``None``
     - Minimum peak height in eV/THz
   * - ``peak_prominence``
     - ``None``
     - Minimum peak prominence in eV/THz
   * - ``peak_min_significance``
     - ``None``
     - Minimum local-noise significance for adaptive peak detection;
       ``4.0`` is a recommended starting value
   * - ``initial_guess_hwhm``
     - ``0.001``
     - Initial HWHM in THz
   * - ``peak_max_hwhm``
     - ``1e6``
     - User hard HWHM bound in THz; an adaptive local bound is also applied
   * - ``modulate_factor``
     - ``0``
     - Samples removed from each side of the detected fit interval
   * - ``re_output_total_freq_lifetime``
     - ``0``
     - Rebuild the combined lifetime file

Fit a few single-Q spectra before enabling all-Q fitting. The current lifetime
file retains MDtrace's existing HWHM conversion convention; users requiring a
quantitative energy-relaxation lifetime should check the linewidth convention
required by their theory or experiment.

Peak strategy, line shape, and baseline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

MDtrace first builds local windows separated by the valleys between detected
peaks. ``fit_peak_strategy = independent`` fits every window separately.
``joint`` groups peaks with broadly overlapping half-height support, while
``auto`` uses a stricter overlap threshold and otherwise keeps the local
fits independent. This avoids joining an entire spectrum merely because
prominence-base intervals overlap.

For a Lorentz fit, one local model is

.. math::

   \Phi(f)
   =
   B(f)
   +
   \sum_i
   \frac{A_i}
        {1+[(f-f_i)/h_i]^2}.

Select the background with, for example,

.. code-block:: text

   fit_baseline_model = constant

The available values are:

``none``
   Use :math:`B(f)=0`. This disables only the explicit background; it does
   not select the legacy fitting-window or parameter-bound behavior.

``constant``
   Fit one non-negative value :math:`B(f)=B_0` per peak cluster.

``linear``
   Fit a non-negative straight line across the cluster interval. Internally,
   MDtrace optimizes the background value at each edge, which prevents the
   fitted background from becoming negative inside the interval.

``auto``
   Fit all three candidates and compare their corrected Akaike information
   criterion (AICc). If candidates are within two AICc units, MDtrace selects
   the simpler baseline. This avoids choosing a slope for an insignificant
   reduction in residual error.

The default is ``auto``. Selected baseline parameters are written to
``<out_files_name>_LORENTZ-<q-index>.baseline``. The fitted figure shows the
individual components, the selected baseline, and their sum.

``fitting_function = dho`` uses the velocity-spectrum damped harmonic
oscillator line shape

.. math::

   D(f)=
   A\frac{(2h)^2 f^2}
   {(f^2-f_0^2)^2+(2hf)^2}.

The reported :math:`h` is half the DHO FWHM, so its weak-damping lifetime is
the same ``1/(2*pi*h)`` convention used for the Lorentz HWHM. In ``auto``
mode MDtrace compares AICc but prefers Lorentz when the DHO damping ratio
``h/f0`` is below 0.05, where the two shapes are practically
indistinguishable. DHO damping regimes and fit-quality flags are written to
``<out_files_name>_LORENTZ-<q-index>.models`` together with the detected peak
significance.
Fitting remains on the original unsmoothed linear SED values.

Select a finite fitting interval with both bounds:

.. code-block:: text

   lorentz_fit_freq_min = 2.0
   lorentz_fit_freq_max = 5.0

Both endpoints are included. The default for both parameters is ``None``. If
neither parameter is written, MDtrace detects and fits peaks over the complete
available frequency interval. The fitted single-Q figure uses the same
displayed frequency range.

Adaptive local-noise peak detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set

.. code-block:: text

   peak_min_significance = 4.0

to enable local-noise-adaptive peak detection. The default is ``None``, which
keeps the original SciPy peak-detection path for backward compatibility.

The complete detection and fitting flow is:

.. code-block:: text

   original linear SED
       |
       v
   take the natural logarithm
       |
       v
   apply a 7-point Hann window to a detection-only copy
       |
       v
   residual = original log SED - smoothed log SED
       |
       v
   estimate local noise with a 31-point rolling MAD
       |
       v
   significance = smoothed-log prominence / local noise
       |
       v
   retain candidates with significance >= peak_min_significance
       |
       v
   refine each candidate to a nearby maximum of the original SED
       |
       v
   fit the original, unsmoothed, linear SED

.. figure:: _static/SED-peak-detection-smoothing-q1.svg
   :alt: Raw and Hann-smoothed log SED with the local residual-noise estimate
   :align: center
   :width: 100%

   Detection-only smoothing and local-noise estimation for Q-point #1 of the
   SrTiO3 example over 0--5 THz. Panel **a** compares the raw log SED with its
   seven-point Hann-smoothed copy. Panel **b** shows the residual
   :math:`r(\omega)` and the local noise band obtained from the 31-point
   rolling MAD. The horizontal coordinate is written as
   :math:`\omega/(2\pi)` because the FFT frequency array is reported in THz.

MDtrace first takes the natural logarithm of the positive SED values and
creates a seven-point Hann-smoothed copy for **peak detection only**. It
estimates the local noise from the difference between the unsmoothed and
smoothed log spectra:

.. math::

   y_\mathrm{raw}(\omega)
   =
   \ln\left[
   \frac{\Phi(\mathbf{q},\omega)}
        {1\,\mathrm{eV\,THz^{-1}}}
   \right],

.. math::

   r(\omega)
   =
   y_\mathrm{raw}(\omega)-y_\mathrm{smooth}(\omega),

.. math::

   \sigma_\mathrm{local}(\omega)
   =
   1.4826\,
   \operatorname{median}_\mathrm{window}
   \left|
   r-\operatorname{median}_\mathrm{window}(r)
   \right|.

The local window contains 31 frequency samples. The factor 1.4826 converts the
median absolute deviation (MAD) to a standard-deviation-like scale for
Gaussian noise. A candidate peak is retained when

.. math::

   \frac{P_\mathrm{log}(\omega_\mathrm{peak})}
        {\sigma_\mathrm{local}(\omega_\mathrm{peak})}
   \ge
   \mathtt{peak\_min\_significance},

where :math:`P_\mathrm{log}` is the prominence measured on the smoothed log
spectrum. Thus, ``peak_min_significance = 4.0`` means that the peak prominence
must be at least four times the locally estimated noise. The parameter and the
reported ``Peak_significance`` values are dimensionless. This robust
signal-to-noise measure is not a formal statistical four-sigma probability,
because neighboring FFT bins and the smoothed data are correlated.

In other words, ``peak_min_significance`` is a local robust signal-to-noise
threshold, not an SED intensity threshold. It adapts to the noise around each
frequency rather than applying one fixed ``eV/THz`` cutoff to every Q point.

For the Q-point #1 spectrum shown above, ``peak_min_significance = 4.0``
retains eight candidates at 0.466667, 0.866667, 1.316667, 1.683333, 2.050000,
2.366667, 2.700000, and 4.200000 THz. Their local significances are 37.66,
15.61, 6.74, 19.43, 8.26, 8.10, 4.11, and 6.98, respectively. The 2.700000
THz candidate is therefore marginal: it only slightly exceeds the threshold
of 4.0.

The logarithm makes the adaptive criterion insensitive to multiplying the
whole spectrum by a constant and helps weak branches on a low background
compete fairly with intense branches. Increasing the value detects fewer,
cleaner peaks; decreasing it detects more weak peaks and more noise.

The existing ``peak_height`` and ``peak_prominence`` parameters remain
available as optional **additional** absolute filters on the original linear
SED, both in eV/THz. To test the new adaptive criterion by itself, leave both
of them as ``None`` or comment them out:

.. code-block:: text

   peak_min_significance = 4.0
   # peak_height = 1.0e-3
   # peak_prominence = 1.0e-4

Only candidate detection uses the Hann-smoothed log spectrum. Peak positions
are returned to nearby maxima of the original SED, and Lorentzian fitting
continues to use the original, unsmoothed, linear SED data. This option does
not yet enforce a minimum peak distance, a minimum peak width, or continuity
between neighboring Q points.

After fitting, the terminal reports frequency and lifetime rather than an
unlabelled HWHM array. The reported lifetime uses the same convention as the
``LORENTZ-*-th-Qpoints.Fre_lifetime`` files:

.. math::

   \tau[\mathrm{ps}]
   =
   \frac{1}
        {2\pi\,\mathrm{HWHM}_f[\mathrm{THz}]}.

DSF parameters
--------------

DSF calculation support is preliminary.

.. list-table::
   :header-rows: 1
   :widths: 23 18 59

   * - Parameter
     - Default
     - Meaning
   * - ``experiment``
     - ``neutron``
     - Probe convention
   * - ``atom_types``
     - ``None``
     - Atom symbols in trajectory type order
   * - ``dsf_qpoints``
     - ``None``
     - Reduced Q-point triples
