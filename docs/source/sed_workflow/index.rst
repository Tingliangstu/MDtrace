SED workflow
============

This chapter explains how MDtrace turns an MD trajectory into total or partial
SED, dispersion and single-Q figures, fitted peak parameters, and
frequency-lifetime summaries. Use it to understand the workflow and output;
use :doc:`../input_parameters` when looking up one keyword.

.. toctree::
   :hidden:
   :maxdepth: 2

   overview
   preparing_trajectory_basis
   computing_plotting
   partial_sed
   Peak detection and line-shape fitting <../peak_detection>
   output_files
   Units and normalization <../sed_units>
   Theory <../theory>

Chapter guide
-------------

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 42 58

   * - Chapter
     - What it explains
   * - :doc:`Overview <overview>`
     - The end-to-end SED workflow, available actions, and recommended order.
   * - :doc:`Preparing the trajectory and basis mapping <preparing_trajectory_basis>`
     - Supported trajectories, sampling consistency, ``basis.in``, primitive
       cells, and commensurate Q paths.
   * - :doc:`Computing and plotting SED <computing_plotting>`
     - NumPy/CuPy execution, timing output, dispersion plots, and single-Q
       spectra.
   * - :doc:`Partial SED <partial_sed>`
     - Element- and direction-resolved spectra and their limitations.
   * - :doc:`Peak detection and line-shape fitting <../peak_detection>`
     - Automatic peak detection, local fit ranges, Lorentz/DHO models, and
       qualitative warnings.
   * - :doc:`Output files <output_files>`
     - Numerical arrays, figures, fitting directories, lifetime data, and the
       trajectory cache.
   * - :doc:`Units and normalization <../sed_units>`
     - Public SED units, one-sided normalization, heatmap color, and slice
       conventions.
   * - :doc:`Theory <../theory>`
     - The SED equations, discrete transform, Q-point construction, and
       linewidth-derived lifetime convention.
