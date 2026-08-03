Preparing the trajectory and basis mapping
==========================================

Trajectory requirements
-----------------------

MDtrace accepts one of the following through
:doc:`../input_parameters/trajectory_file`:

- GPUMD extended XYZ containing positions, velocities, and lattice data;
- one LAMMPS custom dump containing atom IDs, positions, velocities, and box
  information;
- a compatible GPUMD, LAMMPS, or MDtrace NetCDF trajectory.

A suitable LAMMPS dump is

.. code-block:: text

   dump mdtrace all custom ${dump_stride} trajectory.dump id type x y z vx vy vz
   dump_modify mdtrace sort id

Use :doc:`../input_parameters/lammps_unit` to select ``metal``
(Angstrom/ps) or ``real`` (Angstrom/fs). Atom IDs must define the same order in
every frame.

Text trajectories can be converted once to a reusable ``.mdtrace.nc`` cache
or consumed sequentially without an intermediate file. See
:doc:`../input_parameters/trajectory_read_mode` and
:doc:`../input_parameters/trajectory_prefetch`. Native NetCDF input is always
read directly in requested blocks.

Sampling consistency
--------------------

The following values must describe the production trajectory rather than the
equilibration run:

- :doc:`../input_parameters/num_atoms`;
- :doc:`../input_parameters/total_num_steps`;
- :doc:`../input_parameters/time_step`;
- :doc:`../input_parameters/output_data_stride`;
- :doc:`../input_parameters/num_blocks`.

The requested frame count is

.. math::

   N_\mathrm{frames}
   =
   \frac{\mathtt{total\_num\_steps}}
        {\mathtt{output\_data\_stride}},

and must be divisible by ``num_blocks``. The trajectory may contain additional
frames; MDtrace reads only the requested range.

Basis mapping
-------------

``basis.in`` maps each trajectory atom to one repeated primitive cell, one
basis atom, and one mass:

.. code-block:: text

   # MDtrace basis mapping
   atoms_ids unitcell_index basis_index mass_types
   1  1  1  12.011000
   2  1  2  12.011000
   3  2  1  12.011000
   4  2  2  12.011000

Atom IDs, atom count, and masses must agree with the trajectory. Each basis
index must occur exactly once in every repeated cell. The mapping path is set
with :doc:`../input_parameters/basis_lattice_file`.

Primitive cell and Q path
-------------------------

Define the primitive lattice with :doc:`../input_parameters/prim_unitcell`,
the repeated dimensions with :doc:`../input_parameters/supercell_dim`, and an
optional basis transformation with :doc:`../input_parameters/prim_axis`.
For relaxed NPT trajectories, :doc:`../input_parameters/rescale_prim` can
reconstruct a consistently scaled primitive cell.

The requested path is specified by :doc:`../input_parameters/num_qpaths`,
:doc:`../input_parameters/q_path_name`, and
:doc:`../input_parameters/q_path`. MDtrace retains the exact Q points
commensurate with the finite supercell. See :doc:`../theory` for the reciprocal
construction.
