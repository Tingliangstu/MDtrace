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
- fit Lorentz or velocity-DHO peak centers and widths.

MDtrace reads compatible NetCDF trajectories directly. GPUMD extended XYZ and
one-file LAMMPS custom dumps are detected automatically and can either be
streamed directly once during SED computation or converted to a reusable
NetCDF cache. Optional one-block background prefetch is shared by both paths.

Version 1.1.0 supports SED calculation, plotting, and fitting. Dynamic structure
factor (DSF) and electron energy-loss spectroscopy (EELS) are planned future
extensions and are not part of the supported 1.1.0 workflow.
