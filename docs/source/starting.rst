Quick start
===========

Installation check
------------------

.. code-block:: bash

   mdtrace -h

Shared commands
---------------

The supported 1.0 command interface is SED-focused:

.. code-block:: bash

   mdtrace
   mdtrace input.in
   mdtrace -h

With no argument, MDtrace looks for ``input.in`` and then the legacy
``input_SED.in``. The calculation is selected inside the input file:

.. code-block:: text

   action = thinking
   method = sed
   backend = numpy

``thinking`` mode inspects existing SED outputs and runs missing stages.
``compute`` always recalculates and overwrites the main numerical output;
``plot`` and ``fit`` use existing results.

Minimal SED input
-----------------

Create ``input.in``:

.. code-block:: text

   # Common control
   action  = thinking
   method  = sed             # supported 1.0 method
   backend = numpy

   # Trajectory
   trajectory_file    = ../gpumd_run/movie.nc
   out_files_name     = CNT
   time_step          = 1.0
   output_data_stride = 10
   num_blocks         = 5
   max_cores          = 8

   # SED structure
   num_atoms          = 17920
   total_num_steps    = 500000
   basis_lattice_file = ../structure/basis.in
   supercell_dim      = 1 1 160
   prim_unitcell      = 237.433 0 0  0 237.433 0  0 0 2.463
   rescale_prim       = 1

   # SED Q path
   num_qpaths  = 1
   q_path_name = GA
   q_path      = 0 0 0  0 0 1/2

   # Plot
   plot_cutoff_freq   = 50
   plot_interval      = 10
   plot_slice         = 1
   qpoint_slice_index = 0
   if_show_figures    = 0

Run:

.. code-block:: bash

   mdtrace input.in

Trajectory input
----------------

``trajectory_file`` can point to:

- GPUMD extended XYZ containing positions and velocities,
- one LAMMPS custom dump containing atom IDs, positions, and velocities,
- compatible GPUMD, LAMMPS, or MDtrace NetCDF.

Text trajectories are detected automatically, streamed once into a neighboring
``.mdtrace.nc`` file, and reused. NetCDF trajectories are read directly and
only one requested block is loaded at a time.

A suitable LAMMPS dump is:

.. code-block:: text

   dump mdtrace all custom ${dump_stride} trajectory.dump id type x y z vx vy vz
   dump_modify mdtrace sort id

Set ``lammps_unit = metal`` for Angstrom/ps or ``real`` for Angstrom/fs.

Basis mapping
-------------

``basis.in`` maps every trajectory atom to its repeated unit cell and basis
atom:

.. code-block:: text

   # MDtrace basis mapping
   atoms_ids unitcell_index basis_index mass_types
   1  1  1  12.011000
   2  1  2  12.011000
   3  2  1  12.011000
   4  2  2  12.011000

Atom order, atom IDs, masses, and the number of atoms must agree with the
trajectory. Each basis index must occur exactly once per repeated unit cell.

Recommended workflow
--------------------

1. Equilibrate the structure and write a production trajectory containing
   positions, velocities, and cell information.
2. Prepare ``basis.in`` for the same atom order.
3. Choose a commensurate Q path in reduced primitive reciprocal coordinates.
4. Compute the SED with ``action = compute``.
5. Inspect the dispersion and several single-Q slices.
6. Tune peak detection and fitting settings, then use ``action = fit``.

Backends
--------

- ``backend = numpy`` and ``max_cores = 1``: serial NumPy.
- ``backend = numpy`` and ``max_cores > 1``: persistent CPU workers using one
  shared velocity block.
- ``backend = cupy``: one GPU; ``max_cores`` is not used by the SED kernel.

For the optional GPU backend, install the wheel matching the CUDA Toolkit:

.. code-block:: bash

   python -m pip install cupy-cuda12x
   # or
   python -m pip install cupy-cuda13x
