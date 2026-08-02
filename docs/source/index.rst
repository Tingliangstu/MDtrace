MDtrace documentation
=====================

**MDtrace** traces reciprocal-space physics in molecular-dynamics
trajectories. Its production workflow calculates phonon spectral energy
density (SED), plots kinetic-energy-weighted dispersions, decomposes SED by
element and Cartesian direction, and fits spectral peaks with Lorentz or DHO
line shapes. Version 1.0 supports the SED workflow; dynamic structure factor
(DSF) and electron energy-loss spectroscopy (EELS) are future extensions.

Start with :doc:`starting`, then use :doc:`input_parameters` as the current
input-file reference. The public SED unit and plot conventions are defined in
:doc:`sed_units`; equations, normalization, and implementation logic are
described in :doc:`theory`.

.. toctree::
   :maxdepth: 2
   :caption: User manual

   introduction
   installation
   starting
   input_parameters
   peak_detection
   sed_units
   theory
   troubleshooting
   reference
   publications
