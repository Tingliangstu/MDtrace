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

For production SED, prefer a NetCDF trajectory. It is a portable binary
format that stores coordinates, velocities, and cell data together; MDtrace
reads a named ``.nc`` file directly, without first creating an MDtrace cache.
Text trajectories remain useful when a simulation code or an existing workflow
already writes them, but they are substantially larger and slower to parse.

GPUMD
~~~~~

The following is a practical GPUMD production-output block. The NetCDF command
writes every atom (the group ID is ignored because the grouping method is
``-1``), records velocities, and samples every 10 MD steps:

.. code-block:: text

   ensemble       nve
   time_step      1
   dump_thermo    2000
   dump_netcdf    -1 1 10 1 trajectory.nc compression deflate 1

Set ``trajectory_file = trajectory.nc`` and
``output_data_stride = 10`` in ``input.in``. With a 1 fs MD step, this stores
one frame every 10 fs. ``compression deflate 1`` is lossless and is a useful
space/speed compromise. Use ``compression none`` instead when maximum
trajectory write throughput matters more than file size.

The supported text alternative is GPUMD extended XYZ:

.. code-block:: text

   dump_xyz       -1 1 10 trajectory.xyz velocity

It contains the lattice, positions, and velocities needed by SED, but its text
representation costs more storage and read time than NetCDF. See the official
`GPUMD dump_netcdf documentation
<https://gpumd.org/dev/gpumd/input_parameters/dump_netcdf.html>`__ and
`GPUMD dump_xyz documentation
<https://gpumd.org/dev/gpumd/input_parameters/dump_xyz.html>`__ for all
options.

LAMMPS
~~~~~~

Use LAMMPS NetCDF when the LAMMPS build includes the ``NETCDF`` package. For a
simulation using ``units metal`` (Angstrom and ps), a matching SED dump is:

.. code-block:: text

   units          metal
   timestep       0.001
   dump           mdtrace all netcdf 10 trajectory.nc type x y z vx vy vz

Set ``trajectory_file = trajectory.nc`` and
``output_data_stride = 10`` in ``input.in``. MDtrace obtains the coordinate,
velocity, and cell units from the NetCDF metadata. LAMMPS documents this as an
AMBER-style, portable, self-describing binary trajectory. The official
`LAMMPS dump netcdf documentation
<https://docs.lammps.org/dump_netcdf.html>`__ describes package requirements
and the parallel ``netcdf/mpiio`` writer.

For an existing text-based LAMMPS workflow, use one custom dump containing the
atom ID, coordinates, and velocities:

.. code-block:: text

   dump mdtrace all custom ${dump_stride} trajectory.dump id type x y z vx vy vz
   dump_modify mdtrace sort id

Use :doc:`../input_parameters/lammps_unit` to select ``metal``
(Angstrom/ps) or ``real`` (Angstrom/fs). Atom IDs must define the same order in
every frame.

LAMMPS can also write ordinary XYZ files, for example:

.. code-block:: text

   dump           mdtrace_xyz all xyz 10 trajectory.xyz
   dump_modify    mdtrace_xyz element Sr Ti O

That ordinary ``dump xyz`` format is appropriate for visualization, but **not
for MDtrace SED**: it records only the atom label and position, not velocities
or a cell. For text SED input, use the preceding custom dump. Recent LAMMPS
versions also provide ``dump extxyz`` with lattice and velocity fields; it is
useful for interchange and visualization, but the documented, fully supported
LAMMPS text path in MDtrace 1.1.0 is the custom dump above. See the official
`LAMMPS dump documentation <https://docs.lammps.org/dump.html>`__ for XYZ and
ExtXYZ output options.

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
