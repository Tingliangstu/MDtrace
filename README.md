# MDtrace

> Trace the physics inside your molecular-dynamics trajectory.

MDtrace extracts reciprocal-space observables from molecular-dynamics
trajectories. Its current production workflow calculates phonon spectral energy
density (SED), plots kinetic-energy-weighted phonon dispersions, decomposes SED
by element and Cartesian direction, and fits spectral peaks.

Dynamic structure factor (DSF) support is under development.

## Documentation

The complete user guide is available at
[mdtrace.readthedocs.io](https://mdtrace.readthedocs.io/en/latest/).

- [Installation](https://mdtrace.readthedocs.io/en/latest/installation.html)
- [Quick start](https://mdtrace.readthedocs.io/en/latest/starting.html)
- [Input parameters](https://mdtrace.readthedocs.io/en/latest/input_parameters.html)
- [SED theory and implementation](https://mdtrace.readthedocs.io/en/latest/theory.html)
- [Troubleshooting](https://mdtrace.readthedocs.io/en/latest/troubleshooting.html)

## Main features

- GPUMD extended XYZ, LAMMPS custom dump, and compatible NetCDF trajectories
- streaming text-to-NetCDF conversion with reusable block-wise trajectory input
- serial or multi-process NumPy SED calculation
- optional single-GPU CuPy backend
- total and element/Cartesian-resolved SED
- dispersion plotting, Q-point slices, and Lorentzian peak fitting

## Installation

Install the current source:

```bash
git clone https://github.com/Tingliangstu/MDtrace.git
cd MDtrace
python -m pip install .
mdtrace -h
```

For optional GPU acceleration, install the CuPy wheel matching CUDA:

```bash
# Choose one
python -m pip install cupy-cuda12x
python -m pip install cupy-cuda13x
```

The default NumPy backend does not require CUDA or CuPy.

## Quick start

Create `input.in`:

```ini
# Control
action  = thinking
method  = sed
backend = numpy

# Trajectory
trajectory_file    = ../gpumd_run/movie.nc
out_files_name     = CNT
time_step          = 1.0
output_data_stride = 10
num_blocks         = 5
max_cores          = 8

# Structure
num_atoms          = 17920
total_num_steps    = 500000
basis_lattice_file = ../structure/basis.in
supercell_dim      = 1 1 160
prim_unitcell      = 237.433 0 0  0 237.433 0  0 0 2.463
rescale_prim       = 1

# Q path
num_qpaths  = 1
q_path_name = GA
q_path      = 0 0 0  0 0 1/2

```

Run:

```bash
mdtrace input.in
```

`thinking` mode reuses existing results and runs one missing stage at a time:
compute and plot first, then fit on a later run after the spectra can be
inspected. Text trajectories are converted once to a `.mdtrace.nc` file beside
the input file; compatible NetCDF trajectories are read directly in blocks. Set
`action = compute` to recalculate even when numerical output already exists.

Common commands:

```bash
mdtrace                 # input.in, then legacy input_SED.in
mdtrace my_case.in      # explicit input file
mdtrace -h              # command summary
```

## Compute backends

| Configuration | SED execution |
|---|---|
| `backend = numpy`, `max_cores = 1` | Serial NumPy |
| `backend = numpy`, `max_cores > 1` | Persistent CPU workers with shared velocity blocks |
| `backend = cupy` | One GPU per MDtrace process |

See the
[input-parameter reference](https://mdtrace.readthedocs.io/en/latest/input_parameters.html)
for plotting, partial SED, fitting, trajectory conversion, and sampling options.

## Main outputs

| Output | Description |
|---|---|
| `<name>.SED` | Total SED in eV/THz |
| `<name>.Qpts` | Reduced Q-point coordinates |
| `<name>.THz` | Frequency axis |
| `<name>.Q_distances_and_labels` | Path distances and high-symmetry labels |
| `<name>-SED.png` | SED dispersion plot |
| `<name>_partial_SED/` | Optional element/Cartesian files, e.g. `<name>.SED_O_y` |
| `LORENTZ-*.Fre_lifetime` | Current Lorentzian fit output |

The precise HWHM/FWHM lifetime convention is being reviewed. The current
calculation is unchanged; see [TODO.md](TODO.md) before interpreting fitted
lifetimes quantitatively.

## Citation

If MDtrace is used for SED analysis, please cite:

1. T. Liang, W. Jiang, K. Xu, H. Bu, Z. Fan, W. Ouyang, and J. Xu,
   “[PYSED: A tool for extracting kinetic-energy-weighted phonon dispersion and
   lifetime from molecular dynamics simulations](https://doi.org/10.1063/5.0278798),”
   *Journal of Applied Physics* **138**, 075101 (2025).
2. J. A. Thomas, J. E. Turney, R. M. Iutzi, C. H. Amon, and
   A. J. H. McGaughey,
   “[Predicting phonon dispersion relations and lifetimes from the spectral
   energy density](https://doi.org/10.1103/PhysRevB.81.081411),”
   *Physical Review B* **81**, 081411 (2010).

For questions, contact `liangting.zj@gmail.com`.
