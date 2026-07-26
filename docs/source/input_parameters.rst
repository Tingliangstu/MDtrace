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
     - ``thinking``, ``compute``, ``plot``, or ``fit``
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
     - Compression for converted text trajectories; ``0`` favors write speed
   * - ``netcdf_batch_size``
     - ``32``
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
     - Optional fixed color limits
   * - ``use_contourf``
     - ``0``
     - Use filled contours
   * - ``plot_slice``
     - ``0``
     - Plot a single-Q spectrum
   * - ``qpoint_slice_index``
     - ``0``
     - Zero-based Q-point index
   * - ``if_show_figures``
     - ``0``
     - Show figures interactively
   * - ``output_partial``
     - ``0``
     - Save type/element and x/y/z components during compute
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

SED Lorentzian fitting
----------------------

.. list-table::
   :header-rows: 1
   :widths: 27 18 55

   * - Parameter
     - Default
     - Meaning
   * - ``lorentz``
     - ``0``
     - Enable fitting
   * - ``lorentz_fit_all_qpoint``
     - ``0``
     - Fit every Q point
   * - ``lorentz_fit_cutoff``
     - ``None``
     - Highest fitted frequency in THz
   * - ``peak_height``
     - ``None``
     - Minimum peak height
   * - ``peak_prominence``
     - ``None``
     - Minimum peak prominence
   * - ``initial_guess_hwhm``
     - ``0.001``
     - Initial HWHM in THz
   * - ``peak_max_hwhm``
     - ``1e6``
     - Upper HWHM bound in THz
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
