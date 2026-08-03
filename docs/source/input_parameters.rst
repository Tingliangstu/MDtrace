Input parameters
================

MDtrace reads a plain-text control file. The preferred filename is
``input.in``; another path can be supplied on the command line. Each active
line has the form

.. code-block:: text

   parameter_name = value

Blank lines and text following ``#`` are ignored. Run MDtrace with an explicit
file or let it search the current directory for ``input.in`` and then the
legacy ``input_SED.in`` name:

.. code-block:: bash

   mdtrace input.in
   mdtrace

Every public parameter for the supported MDtrace 1.1.0 SED workflow is listed
below. Each parameter name opens a dedicated page containing its syntax,
meaning, default, examples, constraints, and related parameters.

.. toctree::
   :hidden:
   :maxdepth: 4

   input_parameters/common
   input_parameters/sed

Parameter categories
--------------------

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 25 15 60

   * - Category
     - Parameters
     - Contents
   * - :doc:`Common parameters <input_parameters/common>`
     - 17
     - Workflow control, trajectory input, time sampling, data reading,
       performance, and general output.
   * - :doc:`SED parameters <input_parameters/sed>`
     - 27
     - Crystal mapping, Q paths, SED output and plotting, partial
       decomposition, peak detection, fitting, and lifetime output.

Complete parameter index
------------------------

The table is arranged in workflow order. Use the parameter name for its full
reference page or the group name for a smaller task-oriented index.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 25 12 22 16 45

   * - Parameter
     - Scope
     - Group
     - Default
     - Purpose
   * - :doc:`action <input_parameters/action>`
     - Common
     - :doc:`Control <input_parameters/common_control>`
     - ``thinking``
     - Select automatic workflow, compute, plot, or fit.
   * - :doc:`method <input_parameters/method>`
     - Common
     - :doc:`Control <input_parameters/common_control>`
     - ``sed``
     - Select the analysis method; 1.1.0 supports SED.
   * - :doc:`backend <input_parameters/backend>`
     - Common
     - :doc:`Control <input_parameters/common_control>`
     - ``numpy``
     - Select the NumPy or optional CuPy backend.
   * - :doc:`trajectory_file <input_parameters/trajectory_file>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``dump.xyz``
     - Name the XYZ, LAMMPS dump, or NetCDF trajectory.
   * - :doc:`lammps_unit <input_parameters/lammps_unit>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``metal``
     - Select the LAMMPS velocity-unit conversion.
   * - :doc:`num_atoms <input_parameters/num_atoms>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``0``
     - Set the trajectory atom count.
   * - :doc:`total_num_steps <input_parameters/total_num_steps>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``0``
     - Set the production steps represented by the requested data.
   * - :doc:`time_step <input_parameters/time_step>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``0.0``
     - Set the MD integration step in fs.
   * - :doc:`output_data_stride <input_parameters/output_data_stride>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``0``
     - Set the MD steps between saved trajectory frames.
   * - :doc:`num_blocks <input_parameters/num_blocks>`
     - Common
     - :doc:`Trajectory and sampling <input_parameters/common_trajectory>`
     - ``5``
     - Set the number of blocks used for spectral averaging.
   * - :doc:`trajectory_read_mode <input_parameters/trajectory_read_mode>`
     - Common
     - :doc:`I/O and performance <input_parameters/common_io_performance>`
     - ``cache``
     - Choose cached NetCDF conversion or direct text reading.
   * - :doc:`trajectory_prefetch <input_parameters/trajectory_prefetch>`
     - Common
     - :doc:`I/O and performance <input_parameters/common_io_performance>`
     - ``1``
     - Prepare one trajectory block ahead in a background thread.
   * - :doc:`netcdf_batch_size <input_parameters/netcdf_batch_size>`
     - Common
     - :doc:`I/O and performance <input_parameters/common_io_performance>`
     - ``64``
     - Set the number of text-trajectory frames parsed per batch.
   * - :doc:`netcdf_compression_level <input_parameters/netcdf_compression_level>`
     - Common
     - :doc:`I/O and performance <input_parameters/common_io_performance>`
     - ``1``
     - Set zlib compression for converted NetCDF caches.
   * - :doc:`max_cores <input_parameters/max_cores>`
     - Common
     - :doc:`I/O and performance <input_parameters/common_io_performance>`
     - ``4``
     - Limit NumPy worker processes.
   * - :doc:`out_files_name <input_parameters/out_files_name>`
     - Common
     - :doc:`Output and display <input_parameters/common_output>`
     - ``mdtrace``
     - Set the main output prefix.
   * - :doc:`if_show_figures <input_parameters/if_show_figures>`
     - Common
     - :doc:`Output and display <input_parameters/common_output>`
     - ``0``
     - Show saved figures interactively.
   * - :doc:`basis_lattice_file <input_parameters/basis_lattice_file>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``basis.in``
     - Map atoms to repeated cells, basis atoms, and masses.
   * - :doc:`prim_unitcell <input_parameters/prim_unitcell>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``None``
     - Set the primitive-cell lattice vectors.
   * - :doc:`prim_axis <input_parameters/prim_axis>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``None``
     - Apply an optional primitive-axis transformation.
   * - :doc:`supercell_dim <input_parameters/supercell_dim>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``1 1 1``
     - Set supercell repetitions and commensurate Q resolution.
   * - :doc:`rescale_prim <input_parameters/rescale_prim>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``1``
     - Reconstruct the primitive cell from the trajectory cell.
   * - :doc:`num_qpaths <input_parameters/num_qpaths>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``1``
     - Set the number of connected Q-path segments.
   * - :doc:`q_path_name <input_parameters/q_path_name>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``GA``
     - Label the Q-path vertices.
   * - :doc:`q_path <input_parameters/q_path>`
     - SED
     - :doc:`Structure and Q path <input_parameters/sed_structure_qpath>`
     - ``None``
     - Define the Q path in reduced coordinates.
   * - :doc:`output_partial <input_parameters/output_partial>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``0``
     - Save element- and direction-resolved SED components.
   * - :doc:`plot_partial_SED <input_parameters/plot_partial_SED>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - disabled
     - Select an element and optional Cartesian component.
   * - :doc:`plot_cutoff_freq <input_parameters/plot_cutoff_freq>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``None``
     - Set the maximum plotted frequency in THz.
   * - :doc:`plot_interval <input_parameters/plot_interval>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``5.0``
     - Set the frequency-axis tick interval.
   * - :doc:`plot_color <input_parameters/plot_color>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``RdBu_r``
     - Select the dispersion colormap.
   * - :doc:`colorbar_min <input_parameters/colorbar_min>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``None``
     - Set an optional lower logarithmic color limit.
   * - :doc:`colorbar_max <input_parameters/colorbar_max>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``None``
     - Set an optional upper logarithmic color limit.
   * - :doc:`use_contourf <input_parameters/use_contourf>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``0``
     - Draw the SED heatmap with filled contours.
   * - :doc:`plot_slice <input_parameters/plot_slice>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``0``
     - Plot one Q-point spectrum.
   * - :doc:`qpoint_slice_index <input_parameters/qpoint_slice_index>`
     - SED
     - :doc:`SED output and plotting <input_parameters/sed_output_plotting>`
     - ``0``
     - Select the zero-based Q point for plotting or fitting.
   * - :doc:`lorentz_fit_all_qpoint <input_parameters/lorentz_fit_all_qpoint>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``0``
     - Fit every Q point or only the selected Q point.
   * - :doc:`lorentz_fit_freq_min <input_parameters/lorentz_fit_freq_min>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``None``
     - Set the minimum fitted frequency in THz.
   * - :doc:`lorentz_fit_freq_max <input_parameters/lorentz_fit_freq_max>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``None``
     - Set the maximum fitted frequency in THz.
   * - :doc:`fitting_function <input_parameters/fitting_function>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``auto``
     - Select Lorentz, velocity-DHO, or automatic line shape.
   * - :doc:`peak_min_significance <input_parameters/peak_min_significance>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``4.0``
     - Set the local robust significance threshold for peak detection.
   * - :doc:`initial_guess_hwhm <input_parameters/initial_guess_hwhm>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``0.001``
     - Set the optimizer's initial HWHM in THz.
   * - :doc:`peak_max_hwhm <input_parameters/peak_max_hwhm>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``1e6``
     - Set the fitted HWHM upper bound in THz.
   * - :doc:`modulate_factor <input_parameters/modulate_factor>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``0``
     - Remove samples from both ends of each local fit range.
   * - :doc:`re_output_total_freq_lifetime <input_parameters/re_output_total_freq_lifetime>`
     - SED
     - :doc:`Spectral peak fitting <input_parameters/sed_fitting>`
     - ``0``
     - Rebuild combined lifetime output after a single-Q refit.
