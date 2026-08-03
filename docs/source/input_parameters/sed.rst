SED parameters
==============

These parameters apply to the supported SED workflow:

.. code-block:: text

   method = sed

They control crystal mapping, commensurate Q paths, SED output, plotting,
partial decomposition, peak detection, line-shape fitting, and lifetime
output. Every parameter name below opens its complete reference page.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 29 24 16 41

   * - Parameter
     - Group
     - Default
     - Purpose
   * - :doc:`basis_lattice_file <basis_lattice_file>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``basis.in``
     - Map atoms to repeated cells, basis atoms, and masses.
   * - :doc:`prim_unitcell <prim_unitcell>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``None``
     - Set primitive-cell lattice vectors.
   * - :doc:`prim_axis <prim_axis>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``None``
     - Apply an optional primitive-axis transformation.
   * - :doc:`supercell_dim <supercell_dim>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``1 1 1``
     - Set supercell repetitions and commensurate Q resolution.
   * - :doc:`rescale_prim <rescale_prim>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``1``
     - Reconstruct the primitive cell from the trajectory cell.
   * - :doc:`num_qpaths <num_qpaths>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``1``
     - Set the connected path-segment count.
   * - :doc:`q_path_name <q_path_name>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``GA``
     - Label Q-path vertices.
   * - :doc:`q_path <q_path>`
     - :doc:`Structure and Q path <sed_structure_qpath>`
     - ``None``
     - Define reduced-coordinate Q-path vertices.
   * - :doc:`output_partial <output_partial>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``0``
     - Save element- and direction-resolved components.
   * - :doc:`plot_partial_SED <plot_partial_SED>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - disabled
     - Select an element and optional Cartesian component.
   * - :doc:`plot_cutoff_freq <plot_cutoff_freq>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``None``
     - Set the maximum plotted frequency.
   * - :doc:`plot_interval <plot_interval>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``5.0``
     - Set the frequency tick interval.
   * - :doc:`plot_color <plot_color>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``RdBu_r``
     - Select the SED colormap.
   * - :doc:`colorbar_min <colorbar_min>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``None``
     - Set an optional lower color limit.
   * - :doc:`colorbar_max <colorbar_max>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``None``
     - Set an optional upper color limit.
   * - :doc:`use_contourf <use_contourf>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``0``
     - Use filled contours for the dispersion.
   * - :doc:`plot_slice <plot_slice>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``0``
     - Plot one Q-point SED spectrum.
   * - :doc:`qpoint_slice_index <qpoint_slice_index>`
     - :doc:`SED output and plotting <sed_output_plotting>`
     - ``0``
     - Select the zero-based Q point for plotting or fitting.
   * - :doc:`lorentz_fit_all_qpoint <lorentz_fit_all_qpoint>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``0``
     - Fit all Q points or only the selected Q point.
   * - :doc:`lorentz_fit_freq_min <lorentz_fit_freq_min>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``None``
     - Set the minimum fitted frequency.
   * - :doc:`lorentz_fit_freq_max <lorentz_fit_freq_max>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``None``
     - Set the maximum fitted frequency.
   * - :doc:`fitting_function <fitting_function>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``auto``
     - Select Lorentz, velocity-DHO, or automatic line shape.
   * - :doc:`peak_min_significance <peak_min_significance>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``4.0``
     - Set the local robust peak-significance threshold.
   * - :doc:`initial_guess_hwhm <initial_guess_hwhm>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``0.001``
     - Set the initial HWHM for optimization.
   * - :doc:`peak_max_hwhm <peak_max_hwhm>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``1e6``
     - Set the HWHM upper bound.
   * - :doc:`modulate_factor <modulate_factor>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``0``
     - Remove points from both ends of local fit ranges.
   * - :doc:`re_output_total_freq_lifetime <re_output_total_freq_lifetime>`
     - :doc:`Spectral peak fitting <sed_fitting>`
     - ``0``
     - Rebuild combined lifetime output after a single-Q refit.

For method concepts rather than keyword lookup, continue to
:doc:`../sed_workflow/index`.

:doc:`Back to the complete parameter index <../input_parameters>`

.. toctree::
   :hidden:
   :maxdepth: 2

   sed_structure_qpath
   sed_output_plotting
   sed_fitting
