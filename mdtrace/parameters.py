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

"""Common, SED, and DSF input parameter tables."""

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np

from mdtrace.structure.atoms import atomic_masses


@dataclass(frozen=True)
class Parameter:
    """One input parameter: its default value and conversion function."""

    default: object
    read: Callable


# ==================== Value readers ====================

def _one(values):
    if len(values) != 1:
        raise ValueError("requires exactly 1 value")
    return values[0]


def read_text(values):
    return _one(values).strip("'\"")


def read_lower_text(values):
    return read_text(values).lower()


def read_int(values):
    return int(_one(values))


def read_float(values):
    return float(_one(values))


def read_bool(values):
    value = _one(values)
    if value not in {"0", "1"}:
        raise ValueError("must be 0 or 1")
    return value == "1"


def read_optional_float(values):
    value = _one(values)
    return None if value.lower() == "none" else float(value)


def read_text_list(values):
    return [value.strip("'\"") for value in values]


def read_float_list(values):
    return [float(value) for value in values]


def read_int3(values):
    if len(values) != 3:
        raise ValueError("requires 3 values")
    return np.array(values, dtype=int)


def read_matrix3(values):
    if len(values) != 9:
        raise ValueError("requires 9 values")
    return np.array(values, dtype=float).reshape(3, 3)


def _read_number(value):
    """Read a decimal number or a fraction such as ``1/2``."""

    try:
        return float(value)
    except ValueError:
        try:
            return float(Fraction(value))
        except ZeroDivisionError as error:
            raise ValueError("fraction denominator must not be zero") from error


def read_q_path(values):
    return np.array([_read_number(value) for value in values])


def read_partial_sed(values):
    """Read ``plot_partial_SED = element [x|y|z]``."""

    if len(values) not in {1, 2}:
        raise ValueError("requires an element and optional x, y, or z")

    element = values[0].strip("'\"").capitalize()
    if element not in atomic_masses:
        raise ValueError(
            f"element '{values[0]}' was not found in the periodic table"
        )

    direction = values[1].strip("'\"").lower() if len(values) > 1 else None
    if direction not in {None, "x", "y", "z"}:
        raise ValueError("direction must be x, y, or z")
    return True, element, direction


# ==================== Common parameters ====================

common_params = {
    # Control
    "action": Parameter("thinking", read_lower_text),
    "method": Parameter("sed", read_lower_text),
    "backend": Parameter("numpy", read_lower_text),

    # Trajectory and output
    "trajectory_file": Parameter("dump.xyz", read_text),
    "out_files_name": Parameter("mdtrace", read_text),
    "lammps_unit": Parameter("metal", read_lower_text),
    "netcdf_compression_level": Parameter(1, read_int),
    "netcdf_batch_size": Parameter(32, read_int),

    # Trajectory sampling
    "time_step": Parameter(0.0, read_float),
    "output_data_stride": Parameter(0, read_int),

    # Computation
    "num_blocks": Parameter(5, read_int),
    "max_cores": Parameter(4, read_int),

    # Structure shared by SED and DSF
    "prim_unitcell": Parameter(None, read_matrix3),
}


# ==================== SED parameters ====================

sed_params = {
    # MD simulation
    "num_atoms": Parameter(0, read_int),
    "total_num_steps": Parameter(0, read_int),

    # Structure
    "basis_lattice_file": Parameter("basis.in", read_text),
    "supercell_dim": Parameter(np.array([1, 1, 1]), read_int3),
    "prim_axis": Parameter(None, read_matrix3),
    "rescale_prim": Parameter(True, read_bool),

    # Q-points
    "num_qpaths": Parameter(1, read_int),
    "q_path_name": Parameter("GA", read_text),
    "q_path": Parameter(None, read_q_path),

    # Plot
    "plot_cutoff_freq": Parameter(None, read_optional_float),
    "plot_interval": Parameter(5.0, read_float),
    "plot_slice": Parameter(False, read_bool),
    "qpoint_slice_index": Parameter(0, read_int),
    "plot_color": Parameter("RdBu_r", read_text),
    "colorbar_min": Parameter(None, read_optional_float),
    "colorbar_max": Parameter(None, read_optional_float),
    "if_show_figures": Parameter(False, read_bool),
    "use_contourf": Parameter(False, read_bool),
    "output_partial": Parameter(False, read_bool),
    "plot_partial_SED": Parameter(
        (False, None, None),
        read_partial_sed,
    ),

    # Lorentz fit
    "lorentz": Parameter(False, read_bool),
    "lorentz_fit_all_qpoint": Parameter(False, read_bool),
    "lorentz_fit_cutoff": Parameter(None, read_optional_float),
    "peak_height": Parameter(None, read_optional_float),
    "peak_prominence": Parameter(None, read_optional_float),
    "initial_guess_hwhm": Parameter(0.001, read_float),
    "peak_max_hwhm": Parameter(1e6, read_float),
    "modulate_factor": Parameter(0, read_int),
    "re_output_total_freq_lifetime": Parameter(False, read_bool),
}


# ==================== DSF parameters ====================

dsf_params = {
    "experiment": Parameter("neutron", read_lower_text),
    "atom_types": Parameter(None, read_text_list),
    "dsf_qpoints": Parameter(None, read_float_list),
}


# ==================== EELS parameters ====================

# EELS-specific parameters will be added with the calculation method.
eels_params = {}

supported_backends = {"numpy", "cupy"}


# ==================== Validation ====================

def validate_common(params):
    if params.backend not in supported_backends:
        supported = ", ".join(sorted(supported_backends))
        raise ValueError(
            f"backend '{params.backend}' is not available; "
            f"supported backends: {supported}"
        )
    if params.lammps_unit not in {"metal", "real"}:
        raise ValueError("lammps_unit must be 'metal' or 'real'")

    needs_trajectory = (
        params.method in {"sed", "dsf"}
        and params.action in {"thinking", "compute"}
    )
    if needs_trajectory and params.time_step <= 0:
        raise ValueError("time_step must be positive for computation")
    if needs_trajectory and params.output_data_stride <= 0:
        raise ValueError(
            "output_data_stride must be positive for computation"
        )
    if params.time_step < 0:
        raise ValueError("time_step must not be negative")
    if params.output_data_stride < 0:
        raise ValueError("output_data_stride must not be negative")
    if params.num_blocks < 1:
        raise ValueError("num_blocks must be positive")
    if params.max_cores < 1:
        raise ValueError("max_cores must be positive")
    if not 0 <= params.netcdf_compression_level <= 9:
        raise ValueError("netcdf_compression_level must be between 0 and 9")
    if params.netcdf_batch_size < 1:
        raise ValueError("netcdf_batch_size must be positive")


def validate_sed(params):
    """Validate and prepare SED parameters."""

    needs_compute = params.action in {"thinking", "compute"}
    if needs_compute and params.num_atoms <= 0:
        raise ValueError("num_atoms must be positive for SED computation")
    if needs_compute and params.total_num_steps <= 0:
        raise ValueError(
            "total_num_steps must be positive for SED computation"
        )
    if params.num_atoms < 0:
        raise ValueError("num_atoms must not be negative")
    if params.total_num_steps < 0:
        raise ValueError("total_num_steps must not be negative")
    if params.num_qpaths < 1:
        raise ValueError("num_qpaths must be positive")
    if np.any(params.supercell_dim <= 0):
        raise ValueError("supercell_dim values must be positive")

    if needs_compute and params.prim_unitcell is None:
        raise ValueError("prim_unitcell is required for SED computation")
    if params.prim_unitcell is not None:
        if not np.all(np.isfinite(params.prim_unitcell)):
            raise ValueError("prim_unitcell values must be finite")
        if np.isclose(np.linalg.det(params.prim_unitcell), 0.0):
            raise ValueError("prim_unitcell must not be singular")

    if needs_compute and params.q_path is None:
        raise ValueError("q_path is required for SED computation")
    if params.q_path is not None:
        expected = (params.num_qpaths + 1) * 3
        if params.q_path.size != expected:
            raise ValueError(
                f"q_path requires {expected} values for "
                f"num_qpaths = {params.num_qpaths}"
            )
        if not np.all(np.isfinite(params.q_path)):
            raise ValueError("q_path values must be finite")
        if len(params.q_path_name) != params.num_qpaths + 1:
            raise ValueError(
                "q_path_name requires "
                f"{params.num_qpaths + 1} labels for "
                f"num_qpaths = {params.num_qpaths}"
            )

    if needs_compute:
        if params.total_num_steps % params.output_data_stride:
            raise ValueError(
                "total_num_steps must be divisible by "
                "output_data_stride"
            )
        num_frames = (
            params.total_num_steps // params.output_data_stride
        )
        if num_frames < params.num_blocks:
            raise ValueError(
                "the number of trajectory frames must not be smaller "
                "than num_blocks"
            )
        if num_frames % params.num_blocks:
            raise ValueError(
                "the number of trajectory frames must be divisible by "
                "num_blocks"
            )
        if not Path(params.basis_lattice_file).is_file():
            raise ValueError(
                f"input structure '{params.basis_lattice_file}' "
                "was not found"
            )

    (
        params.plot_partial_SED,
        params.plot_partial_element,
        params.plot_partial_dir,
    ) = params.plot_partial_SED

    params.plot_partial_type = None
    if params.plot_partial_SED:
        try:
            masses = np.loadtxt(
                params.basis_lattice_file,
                skiprows=2,
                usecols=3,
            )
        except OSError as error:
            raise ValueError(
                f"input structure '{params.basis_lattice_file}' "
                "was not found"
            ) from error

        unique_masses = np.unique(np.atleast_1d(masses))
        matches = np.flatnonzero(
            np.isclose(
                unique_masses,
                atomic_masses[params.plot_partial_element],
                rtol=0.0,
                atol=5.0e-2,
            )
        )
        if not len(matches):
            raise ValueError(
                f"element '{params.plot_partial_element}' was not found "
                f"in the input structure '{params.basis_lattice_file}'"
        )
        params.plot_partial_type = int(matches[0])

    # Filled later when phonopy eigenvectors are used.
    params.with_eigs = None


def validate_dsf(params):
    if params.dsf_qpoints is not None and len(params.dsf_qpoints) % 3:
        raise ValueError("dsf_qpoints requires groups of 3 values")
    if params.action in {"thinking", "compute"}:
        if not params.atom_types:
            raise ValueError("atom_types is required for DSF computation")
        if not params.dsf_qpoints:
            raise ValueError("dsf_qpoints is required for DSF computation")
        if params.prim_unitcell is None:
            raise ValueError(
                "prim_unitcell is required for DSF computation"
            )


def validate_eels(params):
    """EELS currently has no method-specific parameters."""


# Adding a method requires its parameter table and validator.
methods = {
    "sed": {
        "parameters": sed_params,
        "validate": validate_sed,
    },
    "dsf": {
        "parameters": dsf_params,
        "validate": validate_dsf,
    },
    "eels": {
        "parameters": eels_params,
        "validate": validate_eels,
    },
}


__all__ = ["common_params", "methods", "validate_common"]
