Output files
============

Paths are interpreted from the current working directory. ``out_files_name``
can include a relative directory, but the shared fitting directories are
always ``Fitting-Qpoint/`` and ``Lifetime/`` in the working directory.

Numerical SED and Q-path files
------------------------------

.. list-table::
   :header-rows: 1
   :widths: 38 62

   * - Output
     - Contents
   * - ``<prefix>.SED``
     - SED in ``eV/THz``; rows are positive-frequency bins and columns follow
       the Q-point order in ``<prefix>.Qpts``.
   * - ``<prefix>.Qpts``
     - Retained reduced Q coordinates, one Q point per row.
   * - ``<prefix>.THz``
     - Positive frequency grid in THz.
   * - ``<prefix>.Q_distances_and_labels``
     - Cumulative path distances and labeled high-symmetry vertices.
   * - ``<prefix>-SED.png``
     - Total SED dispersion figure.
   * - ``SED-<q-index>-qpoint.png``
     - Unfitted single-Q spectrum requested with ``plot_slice = 1``.

Partial SED
-----------

With ``output_partial = 1``:

.. code-block:: text

   <prefix>_partial_SED/
   ├── <basename>.SED_<Element>_x
   ├── <basename>.SED_<Element>_y
   ├── <basename>.SED_<Element>_z
   ├── SED_<Element>_xyz.png
   └── SED_<Element>_<direction>-<q-index>-qpoint.png

``basename`` is the final path component of ``out_files_name``. The three
directional matrices use the same row and column conventions as the total SED.

Peak fitting and lifetimes
--------------------------

.. code-block:: text

   Fitting-Qpoint/
   ├── Fitting-0-qpoint.png
   └── Fitting-<q-index>-qpoint.png

   Lifetime/
   ├── Fitting-0-qpoint.Fre_lifetime
   ├── Fitting-<q-index>-qpoint.Fre_lifetime
   └── Fitting-All-Qpoints.Fre_lifetime

   Fitting-Frequency-Lifetime.png

Each per-Q lifetime file contains fitted center frequency in THz and

.. math::

   \tau_\mathrm{SED}[\mathrm{ps}]
   =
   \frac{1}{2\pi\,\mathrm{HWHM}_f[\mathrm{THz}]}.

The combined file concatenates the same two columns in Q-point order. It does
not contain Q index, branch assignment, line-shape model, HWHM, amplitude, or
fit-quality flags; inspect the numbered figures and terminal output for those
details.

For a selected partial SED, ``Fitting-Frequency-Lifetime.png`` is written
inside ``<prefix>_partial_SED/``. Numbered fitting figures and lifetime data
remain in the shared directories above.

Trajectory cache
----------------

For text input with ``trajectory_read_mode = cache``, MDtrace creates or reuses
``<trajectory-name>.mdtrace.nc`` beside the input file. Native NetCDF input and
``trajectory_read_mode = direct`` do not create this cache.
