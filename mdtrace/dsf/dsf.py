# =============================================================================
#     Copyright 2025-2026 Ting Liang and MDTRACE development team
#     This file is part of MDTRACE.
#     MDTRACE is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     MDTRACE is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     You should have received a copy of the GNU General Public License
#     along with MDTRACE.  If not, see <http://www.gnu.org/licenses/>.
# =============================================================================


"""
mdtrace DSF — minimal dynamic structure factor computation.

Pure NumPy implementation backed by the shared NetCDF trajectory reader.
Step 1: single-crystal coherent neutron S(Q,ω) via direct estimator.
"""
import numpy as np

from mdtrace.io.netcdf import NetCDFReader

# ── neutron scattering data (Sears 1992) ────────────────────────

_NEUTRON_COHERENT_LENGTH_FM = {
    "H": -3.7390,  "D": 6.671,   "B": 5.30,    "C": 6.6460,
    "N": 9.36,     "O": 5.803,   "Na": 3.63,   "Al": 3.449,
    "Si": 4.1491,  "P": 5.13,    "S": 2.847,   "Mo": 6.715,
    "Cu": 7.718,   "Se": 7.970,  "Zr": 7.16,   "W": 4.86,
}


def _get_neutron_weights(atom_types):
    """Return coherent scattering lengths for each atom in the supercell."""
    return np.array([_NEUTRON_COHERENT_LENGTH_FM[t] for t in atom_types], dtype=float)


# ── main entry point ────────────────────────────────────────────

def compute_dsf(params):
    """Compute neutron coherent DSF from the prepared trajectory.

    Parameters
    ----------
    params : MDTraceParams
        Parsed input parameters.  Required fields:
        - trajectory_path   : path to the prepared NetCDF trajectory
        - out_files_name    : output prefix
        - dsf_qpoints       : Q-points in fractional coords (flat list)
        - atom_types        : list of atom type labels
        - num_blocks        : number of blocks for averaging and SEM
        - time_step         : MD time step (fs)
        - output_data_stride: data output stride
        - prim_unitcell     : 3×3 primitive cell (Angstrom)

    Returns
    -------
    dict with keys:
        q_cart      : Q-points in Cartesian (1/Angstrom)
        freq_thz    : frequency grid (THz)
        sqw         : S(Q,ω) mean
        sqw_sem     : S(Q,ω) standard error
        q_frac      : input Q-points in fractional coords
    """
    with NetCDFReader(params.trajectory_path) as trajectory:
        trajectory.require("positions")
        n_frames = trajectory.info.n_frames
        n_atoms = trajectory.info.n_atoms
    print(f"  Trajectory: {n_frames} frames × {n_atoms} atoms")

    # ── resolve atom types ──
    atom_types = params.atom_types
    if atom_types is None:
        raise ValueError(
            "atom_types not set in input.in.\n"
            "Add:  atom_types = Si  (or Mo S S, etc.)"
        )

    # Expand per-type → per-atom if needed
    if len(atom_types) < n_atoms:
        # atom_types gives the list of UNIQUE types
        # we need per-atom; assume types repeat in order
        unique_types = list(dict.fromkeys(atom_types))
        if n_atoms % len(unique_types) != 0:
            raise ValueError(
                f"atom_types length ({len(atom_types)}) does not divide "
                f"num_atoms ({n_atoms}). Provide per-atom types or exact unique types."
            )
        # For now, assume supercell = (na, nb, nc) × primitive with unique types
        # We'll expand assuming each unique type has equal count
        atoms_per_type = n_atoms // len(unique_types)
        per_atom_types = []
        for t in unique_types:
            per_atom_types.extend([t] * atoms_per_type)
        atom_types = per_atom_types

    if len(atom_types) != n_atoms:
        raise ValueError(
            f"atom_types count ({len(atom_types)}) != num_atoms ({n_atoms}). "
            "Provide one label per atom or unique type list."
        )

    # ── neutron weights ──
    weights = _get_neutron_weights(atom_types)
    print(f"  Neutron weights: {dict(zip(*np.unique(atom_types, return_counts=True)))}")

    # ── Q-points: fractional → Cartesian ──
    dsf_q_raw = params.dsf_qpoints
    if dsf_q_raw is None:
        raise ValueError("dsf_qpoints not set in input.in")

    q_frac = np.array(dsf_q_raw).reshape(-1, 3)
    n_q = q_frac.shape[0]

    # primitive cell for Cartesian conversion
    if params.prim_unitcell is not None:
        cell = params.prim_unitcell
    else:
        # fallback: identity
        cell = np.eye(3)

    # fractional → Cartesian: Q_cart = 2π * (q_frac @ cell⁻¹) ?
    # Actually: Q_cart = 2π * q_frac @ reciprocal_lattice
    # reciprocal_lattice = 2π * inv(cell).T... no:
    # b1 = 2π * (a2×a3) / (a1·(a2×a3))  but for SED convention we use:
    # Q_cart (Angstrom⁻¹) = 2π * q_frac @ inv(cell).T
    # Check: if cell = diag(a,a,a), then Q = (2π/a) * (h,k,l)
    inv_cell = np.linalg.inv(cell)
    q_cart = 2.0 * np.pi * (q_frac @ inv_cell.T)

    print(f"  Q-points ({n_q}):")
    for i, (qf, qc) in enumerate(zip(q_frac, q_cart)):
        print(f"    [{i}] frac: {qf}  →  cart: [{qc[0]:.4f}, {qc[1]:.4f}, {qc[2]:.4f}] 1/Å")

    # ── frequency grid ──
    block_size = n_frames // params.num_blocks
    if block_size < 2:
        block_size = n_frames
        num_blocks = 1
    else:
        num_blocks = params.num_blocks

    dt_sec = params.time_step * params.output_data_stride / 1e15  # fs → s
    freq_hz = np.fft.fftfreq(block_size, dt_sec)
    # positive frequencies only (skip DC for plotting convenience)
    pos_mask = freq_hz > 0
    freq_thz = freq_hz[pos_mask] / 1e12

    # ── block-averaged DSF ──
    all_blocks = []
    with NetCDFReader(params.trajectory_path) as trajectory:
        for block_idx in range(num_blocks):
            start = block_idx * block_size
            end = start + block_size
            if end > n_frames:
                break
            block = trajectory.read_positions(slice(start, end))

            sqw_block = np.zeros((n_q, len(freq_thz)))
            for iq, q_vec in enumerate(q_cart):
                # ρ(Q, t) = Σ w_a exp(i Q·r_a(t))
                phase = np.exp(1j * np.dot(block, q_vec))  # (T, N)
                rho = np.sum(weights[None, :] * phase, axis=1)  # (T,)

                # FFT with forward normalization (1/√N convention)
                rho_fft = np.fft.fft(rho, norm="forward")  # (T,)
                spectrum = np.abs(rho_fft[pos_mask]) ** 2

                # normalize: divide by N * N_t
                sqw_block[iq] = spectrum / (n_atoms * block_size)

            all_blocks.append(sqw_block)

    all_blocks = np.array(all_blocks)  # (num_blocks, n_q, n_freq)
    sqw_mean = np.mean(all_blocks, axis=0)
    sqw_sem = np.std(all_blocks, axis=0, ddof=1) / np.sqrt(all_blocks.shape[0]) \
              if all_blocks.shape[0] > 1 else np.zeros_like(sqw_mean)

    print(f"  DSF shape: {n_q} Q-points × {len(freq_thz)} frequencies")
    print(f"  Blocks: {all_blocks.shape[0]}, SEM computed: {all_blocks.shape[0] > 1}")

    return {
        "q_cart": q_cart,
        "q_frac": q_frac,
        "freq_thz": freq_thz,
        "sqw": sqw_mean,
        "sqw_sem": sqw_sem,
    }


# ── output ──────────────────────────────────────────────────────

def save_dsf(result, params):
    """Save DSF result to text files."""
    prefix = params.out_files_name

    # S(Q,ω) matrix: rows = Q-points, columns = frequencies
    np.savetxt(prefix + ".dsf", result["sqw"],
               header=f"S(Q,w) — {result['sqw'].shape[0]} Q-points × "
                      f"{result['sqw'].shape[1]} frequencies")

    # frequency grid
    np.savetxt(prefix + ".dsf_THz", result["freq_thz"],
               header="Frequency (THz)")

    # Q-points (Cartesian, 1/Angstrom)
    np.savetxt(prefix + ".dsf_Qcart", result["q_cart"],
               header="Q-points (Cartesian, 1/Angstrom)")

    # Q-points (fractional)
    np.savetxt(prefix + ".dsf_Qfrac", result["q_frac"],
               header="Q-points (fractional)")

    # SEM
    np.savetxt(prefix + ".dsf_sem", result["sqw_sem"],
               header="S(Q,w) standard error of the mean")

    print(f"  Saved: {prefix}.dsf, .dsf_THz, .dsf_Qcart, .dsf_Qfrac, .dsf_sem")
