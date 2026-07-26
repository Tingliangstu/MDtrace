Introduction
============

MDtrace extracts reciprocal-space observables from molecular-dynamics
trajectories. Its current production workflow calculates phonon spectral energy
density (SED), which shows how kinetic energy is distributed over wave vector
and frequency.

The SED workflow can:

- construct exact Q points commensurate with a finite MD supercell,
- calculate total or element/direction-resolved SED,
- use serial NumPy, shared-memory multiprocessing, or optional CuPy,
- plot phonon dispersions and individual Q-point spectra,
- fit Lorentzian peak centers and widths.

MDtrace reads compatible NetCDF trajectories directly. GPUMD extended XYZ and
one-file LAMMPS custom dumps are detected automatically, converted once to a
neighboring NetCDF file, and reused.

Dynamic structure factor (DSF) calculation support is preliminary. The manual
therefore separates shared commands and trajectory settings from SED-specific
parameters, leaving a clean place for future DSF documentation.
