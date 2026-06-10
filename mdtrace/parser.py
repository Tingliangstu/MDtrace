"""
mdtrace input parser — clean action/method/backend dispatch.

Backward-compatible with legacy pySED plot_SED input format.
"""
import os
import warnings
import numpy as np
from fractions import Fraction


def parse_float_or_fraction(token):
    try:
        return float(token)
    except ValueError:
        return float(Fraction(token))


class MDTraceParams:
    """Parsed input parameters for mdtrace."""

    def __init__(self, input_file="input.in"):

        self.input_file = input_file

        # ==================== Control ====================
        self.action = "thinking"
        self.method = "sed"
        self.backend = "numpy"

        # ==================== MD simulation ====================
        self.num_atoms = 0
        self.total_num_steps = 0
        self.time_step = 0.0
        self.output_data_stride = 0
        self.file_format = "gpumd"

        # ==================== I/O ====================
        self.dump_xyz_file = "dump.xyz"
        self.pos_file = "pos.dat"
        self.vels_file = "vels.dat"
        self.basis_lattice_file = "basis.in"
        self.output_hdf5 = "vel_pos_compress.hdf5"
        self.out_files_name = "mdtrace"
        self.lammps_unit = "metal"

        # ==================== Structure ====================
        self.supercell_dim = np.array([1, 1, 1])
        self.prim_unitcell = None
        self.prim_axis = None
        self.rescale_prim = 1

        # ==================== Computation ====================
        self.compress = 1
        self.num_splits = 1
        self.use_parallel = 1
        self.max_cores = 4

        # ==================== Q-points ====================
        self.num_qpaths = 1
        self.q_path_name = "GA"
        self.q_path = None

        # ==================== Plot ====================
        self.plot_cutoff_freq = None
        self.plot_interval = 5.0
        self.plot_slice = 0
        self.qpoint_slice_index = 0
        self.q_slice_index = 0           # alias for backward compat
        self.plot_color = "RdBu_r"
        self.colorbar_min = None
        self.colorbar_max = None
        self.if_show_figures = 0
        self.use_contourf = 0

        # ==================== Lorentz fit ====================
        self.lorentz = 0
        self.lorentz_fit_all_qpoint = 0
        self.lorentz_fit_cutoff = None
        self.peak_height = None
        self.peak_prominence = None
        self.initial_guess_hwhm = 0.001
        self.peak_max_hwhm = 1e6
        self.modulate_factor = 0
        self.re_output_total_freq_lifetime = 0

        # ==================== DSF ====================
        self.experiment = "neutron"
        self.atom_types = None
        self.dsf_qpoints = None
        self.dsf_num_blocks = 5

        # ==================== Internal ====================
        self.with_eigs = None
        self._action_set_explicitly = False
        self._legacy_plot_sed = None

        # Parse
        self._pending_q_path_tokens = None
        self._parse(input_file)

    # ── key lookup ──────────────────────────────────────────────
    @property
    def _allowed_keys(self):
        return {
            # control
            "action", "method", "backend",
            # MD
            "num_atoms", "total_num_steps", "time_step", "output_data_stride",
            "file_format", "lammps_unit",
            # I/O
            "dump_xyz_file", "pos_file", "vels_file", "basis_lattice_file",
            "output_hdf5", "out_files_name",
            # structure
            "supercell_dim", "prim_unitcell", "prim_axis", "rescale_prim",
            # computation
            "compress", "num_splits", "use_parallel", "max_cores",
            # Q-points
            "num_qpaths", "q_path_name", "q_path",
            # plot
            "plot_cutoff_freq", "plot_interval", "plot_slice",
            "qpoint_slice_index", "plot_color", "colorbar_min", "colorbar_max",
            "if_show_figures", "use_contourf",
            # lorentz
            "lorentz", "lorentz_fit_all_qpoint", "lorentz_fit_cutoff",
            "peak_height", "peak_prominence", "initial_guess_hwhm",
            "peak_max_hwhm", "modulate_factor", "re_output_total_freq_lifetime",
            # DSF
            "experiment", "atom_types", "dsf_qpoints", "dsf_num_blocks",
            # legacy (deprecated but accepted)
            "plot_SED", "output_partial", "plot_partial_SED",
        }

    # ── parse ───────────────────────────────────────────────────
    def _parse(self, input_file):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found.")

        with open(input_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            clean = line.split("#", 1)[0].strip()
            if not clean:
                continue
            tokens = clean.split()
            if not tokens:
                continue
            key = tokens[0].lstrip("﻿")

            if key not in self._allowed_keys:
                self._warn(f"unknown parameter '{key}' — ignored")
                continue

            self._set_param(key, tokens)

        # resolve pending q_path
        if self._pending_q_path_tokens is not None and self.num_qpaths:
            needed = (self.num_qpaths + 1) * 3
            if len(self._pending_q_path_tokens) < needed:
                raise ValueError("q_path: not enough values")
            vals = [parse_float_or_fraction(t) for t in self._pending_q_path_tokens[:needed]]
            self.q_path = np.array(vals).reshape(self.num_qpaths + 1, 3)

        # ── backward compatibility ─────────────────────────
        self._resolve_legacy()

    def _set_param(self, key, tokens):
        """Dispatch a single key=value(...) line."""
        idx = tokens.index("=") if "=" in tokens else -1
        if idx < 0:
            return
        vals = tokens[idx + 1:]

        def _first():
            return vals[0]

        # control
        if key == "action":
            self.action = _first()
            self._action_set_explicitly = True
        elif key == "method":
            self.method = _first()
        elif key == "backend":
            self.backend = _first()

        # MD
        elif key == "num_atoms":
            self.num_atoms = int(_first())
        elif key == "total_num_steps":
            self.total_num_steps = int(_first())
        elif key == "time_step":
            self.time_step = float(_first())
        elif key == "output_data_stride":
            self.output_data_stride = int(_first())
        elif key == "file_format":
            self.file_format = _first().strip("'\"")
        elif key == "lammps_unit":
            self.lammps_unit = _first().strip("'\"")

        # I/O
        elif key == "dump_xyz_file":
            self.dump_xyz_file = _first().strip("'\"")
        elif key == "pos_file":
            self.pos_file = _first().strip("'\"")
        elif key == "vels_file":
            self.vels_file = _first().strip("'\"")
        elif key == "basis_lattice_file":
            self.basis_lattice_file = _first().strip("'\"")
        elif key == "output_hdf5":
            self.output_hdf5 = _first().strip("'\"")
        elif key == "out_files_name":
            self.out_files_name = _first().strip("'\"")

        # structure
        elif key == "supercell_dim":
            self.supercell_dim = np.array(vals[:3]).astype(int)
        elif key == "prim_unitcell":
            self.prim_unitcell = np.array([float(x) for x in vals[:9]]).reshape(3, 3)
        elif key == "prim_axis":
            self.prim_axis = np.array([float(x) for x in vals[:9]]).reshape(3, 3)
        elif key == "rescale_prim":
            self.rescale_prim = bool(int(_first()))

        # computation
        elif key == "compress":
            self.compress = bool(int(_first()))
        elif key == "num_splits":
            self.num_splits = int(_first())
        elif key == "use_parallel":
            self.use_parallel = bool(int(_first()))
        elif key == "max_cores":
            self.max_cores = int(_first())

        # Q-points
        elif key == "num_qpaths":
            self.num_qpaths = int(_first())
        elif key == "q_path_name":
            self.q_path_name = _first().strip("'\"")
        elif key == "q_path":
            self._pending_q_path_tokens = vals

        # plot
        elif key == "plot_cutoff_freq":
            self.plot_cutoff_freq = float(_first()) if _first().lower() != "none" else None
        elif key == "plot_interval":
            self.plot_interval = float(_first())
        elif key == "plot_slice":
            self.plot_slice = bool(int(_first()))
        elif key == "qpoint_slice_index":
            val = int(_first())
            self.qpoint_slice_index = val
            self.q_slice_index = val        # alias for backward compat
        elif key == "plot_color":
            self.plot_color = _first().strip("'\"")
        elif key == "colorbar_min":
            self.colorbar_min = float(_first()) if _first().lower() != "none" else None
        elif key == "colorbar_max":
            self.colorbar_max = float(_first()) if _first().lower() != "none" else None
        elif key == "if_show_figures":
            self.if_show_figures = bool(int(_first()))
        elif key == "use_contourf":
            self.use_contourf = bool(int(_first()))

        # lorentz
        elif key == "lorentz":
            self.lorentz = bool(int(_first()))
        elif key == "lorentz_fit_all_qpoint":
            self.lorentz_fit_all_qpoint = bool(int(_first()))
        elif key == "lorentz_fit_cutoff":
            self.lorentz_fit_cutoff = float(_first()) if _first().lower() != "none" else None
        elif key == "peak_height":
            self.peak_height = float(_first()) if _first().lower() != "none" else None
        elif key == "peak_prominence":
            self.peak_prominence = float(_first()) if _first().lower() != "none" else None
        elif key == "initial_guess_hwhm":
            self.initial_guess_hwhm = float(_first())
        elif key == "peak_max_hwhm":
            self.peak_max_hwhm = float(_first())
        elif key == "modulate_factor":
            self.modulate_factor = int(_first())
        elif key == "re_output_total_freq_lifetime":
            self.re_output_total_freq_lifetime = bool(int(_first()))

        # DSF
        elif key == "experiment":
            self.experiment = _first()
        elif key == "atom_types":
            self.atom_types = [v.strip("'\"") for v in vals]
        elif key == "dsf_qpoints":
            self.dsf_qpoints = [float(v) for v in vals]
        elif key == "dsf_num_blocks":
            self.dsf_num_blocks = int(_first())

        # legacy
        elif key == "plot_SED":
            self._legacy_plot_sed = int(_first())
        elif key == "output_partial":
            pass  # silently accept, mdtrace may re-implement later
        elif key == "plot_partial_SED":
            pass

    # ── backward compatibility ─────────────────────────────────
    def _resolve_legacy(self):
        """Convert old plot_SED flag to new action/method."""
        if self._legacy_plot_sed is not None:
            if not self._action_set_explicitly:
                if self._legacy_plot_sed == 0:
                    self.action = "compute"
                elif self.lorentz:
                    self.action = "fit"
                else:
                    self.action = "plot"
            self._warn(
                "plot_SED is deprecated. Use:\n"
                "  action = compute   (was plot_SED = 0)\n"
                "  action = plot      (was plot_SED = 1, lorentz = 0)\n"
                "  action = fit       (was plot_SED = 1, lorentz = 1)\n"
                "  action = thinking  (auto-detect, recommended)"
            )

    # ── helpers ─────────────────────────────────────────────────
    @staticmethod
    def _warn(msg):
        warnings.warn(f"\n⚠  {msg}\n", FutureWarning, stacklevel=3)


def read_input(input_file="input.in"):
    """Read and parse an mdtrace input file. Returns MDTraceParams."""
    return MDTraceParams(input_file)
