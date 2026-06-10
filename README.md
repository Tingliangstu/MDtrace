# mdtrace — MD trajectory Trace

> **Trace the physics inside your MD trajectory.**

**mdtrace** extracts multiple experimental observables from a single molecular dynamics trajectory: phonon spectral energy density (SED), dynamic structure factors \(S(\mathbf{Q},\omega)\), electron energy-loss spectra, and more.

---

## Main features

- **phonon SED** — compute kinetic-energy-weighted phonon dispersion and extract phonon lifetimes via Lorentzian fitting
- **Dynamic structure factor** — neutron / X-ray coherent and incoherent \(S(\mathbf{Q},\omega)\) via the direct density-amplitude estimator
- **thinking mode** — auto-detects progress and runs the next needed step; write your input once and just `mdtrace input.in`
- **High-quality SED plots** with customizable colormaps and q-slice views
- **Batch Lorentzian fitting** — fit all q-points at once and output phonon lifetimes, or fit individual q-points
- **Multi-threaded parallelism** for fast computation
- **GPU support** *(coming soon via CuPy backend)*
- Interfaces with **GPUMD** and **LAMMPS** trajectories; captures quantum dynamics from path-integral MD

---

## Installation

### From source (recommended)

```bash
git clone https://github.com/Tingliangstu/mdtrace.git
cd mdtrace
pip install .
```

Verify:

```bash
mdtrace -h
```

### One-line install via pip

```bash
pip install git+https://github.com/Tingliangstu/mdtrace.git
```

### From PyPI *(coming soon)*

```bash
pip install mdtrace
```

---

## Quick start

Create an `input.in` file:

```ini
action      = thinking
method      = sed

num_atoms          = 16000
total_num_steps    = 100000
time_step          = 1
output_data_stride = 20
file_format        = gpumd
dump_xyz_file      = dump.xyz
basis_lattice_file = basis.in
out_files_name     = my_system
output_hdf5        = vel_pos_compress.hdf5

supercell_dim  = 20 20 20
prim_unitcell  = 3.867 0 0 1.933 3.349 0 1.933 1.116 3.157
rescale_prim   = 1

num_qpaths  = 5
q_path_name = GXUKGL
q_path      = 0.0 0.0 0.0  0.5 0.0 0.5  0.625 0.25 0.625  0.375 0.375 0.75  0.0 0.0 0.0  0.5 0.5 0.5

compress     = 1
num_splits   = 5
use_parallel = 1
max_cores    = 4

lorentz                = 1
lorentz_fit_all_qpoint = 1
peak_height            = 1.0e-6
peak_prominence        = 2.0e-6
```

Then run:

```bash
mdtrace input.in
```

**thinking mode** will automatically compress → compute SED → plot → fit Lorentzian peaks. Each subsequent run picks up where it left off.

For DSF:

```ini
action      = thinking
method      = dsf

# ... (same MD & structure settings as above)

experiment     = neutron
atom_types     = Si
dsf_qpoints    = 0.0 0.0 0.0  0.5 0.0 0.0  0.0 0.5 0.0
dsf_num_blocks = 5
```

---

## Usage

```bash
mdtrace              # looks for input.in (or input_SED.in for legacy)
mdtrace my_input.in  # use a specific input file
mdtrace -h           # full help with all parameters
```

### Control parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `action` | `thinking` / `compute` / `plot` / `fit` | What to do. `thinking` auto-detects (recommended) |
| `method` | `sed` / `dsf` / `eels` | Which observable to compute |
| `backend` | `numpy` / `cupy` | CPU or GPU backend |

---

## Citations

If you use **mdtrace** in your research, please cite:

- **[1]** T. Liang, W. Jiang, K. Xu, H. Bu, Z. Fan, W. Ouyang, J. Xu, *PYSED: A tool for extracting kinetic-energy-weighted phonon dispersion and lifetime from molecular dynamics simulations*, J. Appl. Phys. **138**, 075101 (2025). — *for any work that used mdtrace (SED method)*
- **[2]** J. A. Thomas, J. E. Turney, R. M. Iutzi, C. H. Amon, A. J. H. McGaughey, *Predicting phonon dispersion relations and lifetimes from the spectral energy density*, Phys. Rev. B **81**, 081411 (2010). — *fundamental theory on phonon SED*

---

## Examples

Example input files are provided in the `example/` directory. Reproducing these cases is the best way to learn mdtrace before applying it to your own systems.

---

## Documentation

Full documentation is available at [https://pysed.readthedocs.io](https://pysed.readthedocs.io) (pySED docs; mdtrace-specific docs coming soon).
