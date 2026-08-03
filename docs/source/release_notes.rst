Release notes
=============

Version 1.1.0
-------------

MDtrace 1.1.0 streamlines the documented SED workflow. Its supported public
scope remains SED calculation, plotting, and
spectral peak fitting.

Trajectory input and performance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- GPUMD XYZ, one-file LAMMPS dumps, converted NetCDF caches, and native
  NetCDF trajectories now use one block-oriented SED input interface.
- ``trajectory_read_mode = cache | direct`` lets text trajectories either
  create/reuse a NetCDF cache or be scanned sequentially once without an
  intermediate file.
- ``trajectory_prefetch = 1`` is enabled by default and reads at most one
  block ahead in a single background thread. It may reduce SED wall time when
  trajectory input is the bottleneck, at the cost of one additional raw block
  in CPU memory.
- The CuPy timing output distinguishes the six explicitly measured operations,
  other SED work, initial trajectory/setup time, SED calculation, and
  output/finalization.

Peak detection and fitting
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Peak detection uses a dimensionless local prominence-to-noise threshold,
  ``peak_min_significance``, based on a detection-only smoothed log spectrum
  and rolling MAD noise estimate.
- Every detected peak is fitted independently over its local basin with a
  zero background.
- ``fitting_function = lorentz | dho | auto`` supports Lorentz and
  velocity-spectrum DHO line shapes. ``auto`` compares candidates with AICc
  while retaining Lorentz in the practically indistinguishable weak-damping
  limit.
- Per-Q fitting figures are written under ``Fitting-Qpoint/``; per-Q and
  combined frequency-lifetime data are written under ``Lifetime/``; and the
  all-Q summary is ``Fitting-Frequency-Lifetime.png``.
- Reported times use
  :math:`\tau_\mathrm{SED}=1/(2\pi\,\mathrm{HWHM}_{f})`. Incomplete,
  overlapping, critically damped, and overdamped features remain qualitative
  linewidth-derived times rather than guaranteed transport lifetimes.

Packaging and compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The supported interpreter floor is Python 3.10.
- Package metadata, the CLI banner, and Sphinx now read the same
  ``mdtrace/version.py`` value, ``1.1.0``.
- Source and wheel distributions include the GPL-3.0-or-later license, the
  current README, and the unified trajectory modules; the installable wheel
  excludes the repository test package.
- Every supported common or SED input parameter has a dedicated reference
  page, and the documentation dependencies are fixed for reproducible tagged
  builds.

Documentation versions
----------------------

``latest`` follows the ``main`` branch and may include changes made after a
release. ``1.1.0`` is the immutable documentation snapshot built from the
``1.1.0`` Git tag. Use the Read the Docs version selector when reproducibility
requires the manual that matches an installed release. Read the Docs may also
publish ``stable`` as an alias for the newest stable tag; it is not a separate
source manual. The standalone ``main`` version can remain inactive because
``latest`` already tracks that branch.

DSF, EELS, and mode-projected SED remain roadmap items and are not part of the
supported 1.1.0 command interface.
