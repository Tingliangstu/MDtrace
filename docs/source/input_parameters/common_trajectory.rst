Trajectory and sampling
=======================

These parameters identify the trajectory and convert the MD sampling schedule
into the frames and frequency range used by MDtrace.

.. list-table::
   :class: parameter-index
   :header-rows: 1
   :widths: 28 18 54

   * - Parameter
     - Default
     - Purpose
   * - :doc:`trajectory_file <trajectory_file>`
     - ``dump.xyz``
     - Name the GPUMD XYZ, LAMMPS dump, or NetCDF trajectory.
   * - :doc:`lammps_unit <lammps_unit>`
     - ``metal``
     - Select the LAMMPS velocity-unit conversion.
   * - :doc:`num_atoms <num_atoms>`
     - ``0``
     - Set the number of atoms in every requested frame.
   * - :doc:`total_num_steps <total_num_steps>`
     - ``0``
     - Set the MD production steps represented by the requested frames.
   * - :doc:`time_step <time_step>`
     - ``0.0``
     - Set the MD integration step in fs.
   * - :doc:`output_data_stride <output_data_stride>`
     - ``0``
     - Set the number of MD steps between saved frames.
   * - :doc:`num_blocks <num_blocks>`
     - ``5``
     - Split the requested frames for spectral averaging.

The number of requested frames is

.. math::

   N_\mathrm{frames}
   =
   \frac{\mathtt{total\_num\_steps}}
        {\mathtt{output\_data\_stride}},

and must be divisible by ``num_blocks``. See the individual pages for the
Nyquist limit and block-dependent frequency resolution.

:doc:`Back to Common parameters <common>`

.. toctree::
   :hidden:

   trajectory_file
   lammps_unit
   num_atoms
   total_num_steps
   time_step
   output_data_stride
   num_blocks
