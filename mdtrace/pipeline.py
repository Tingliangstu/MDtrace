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
mdtrace pipeline — thinking-mode workflow with auto-detect progress.

Each step checks whether its output already exists before running.
thinking mode chains all needed steps; individual actions force one step.
"""
import os
import sys
import time
from pathlib import Path

from mdtrace.io.prepare import prepare_trajectory
from mdtrace.sed import FileIO, Lorentz, Phonon, Plot_SED, construct_BZ

# ── step detectors ──────────────────────────────────────────────

def _sed_ready(params):
    return os.path.exists(params.out_files_name + ".SED")


def _qpts_ready(params):
    return os.path.exists(params.out_files_name + ".Qpts")


def _thz_ready(params):
    return os.path.exists(params.out_files_name + ".THz")


def _plot_data_ready(params):
    return _sed_ready(params) and _qpts_ready(params) and _thz_ready(params)


def _fit_ready(params):
    return os.path.exists("TOTAL-LORENTZ-Qpoints.Fre_lifetime")


def _dsf_ready(params):
    return os.path.exists(params.out_files_name + ".dsf")


# ── step runners ────────────────────────────────────────────────

def step_prepare_trajectory(params):
    """Resolve every supported trajectory to one readable NetCDF file."""
    source = Path(params.trajectory_file)

    t0 = time.perf_counter()
    prepared, source_format = prepare_trajectory(
        source=source,
        lammps_unit=params.lammps_unit,
        batch_size=params.netcdf_batch_size,
        compression_level=params.netcdf_compression_level,
    )
    params.source_format = source_format
    params.trajectory_path = str(prepared)
    elapsed = time.perf_counter() - t0
    if prepared == source:
        print(f"  ✓  Reading NetCDF trajectory: {prepared}")
    else:
        print(f"  ✓  Trajectory ready: {prepared} ({elapsed:.1f} s)")


def step_compute_sed(params):
    """Compute phonon SED."""
    if _sed_ready(params):
        print(f"  ✓  {params.out_files_name}.SED  already exists — skipping compute")
        return

    print("  ▶  Computing phonon SED ...")
    t0 = time.perf_counter()

    BZ_info = construct_BZ.BZ_methods(params)
    sed = Phonon.spectral_energy_density(params)
    sed.compute_sed(params, BZ_info)

    # Some parallel workers may leave dangling imports; silence them
    sys.stdout.flush()

    FileIO.write_output(sed, params, BZ_info)
    elapsed = time.perf_counter() - t0
    print(f"  ✓  SED compute done ({elapsed:.1f} s)")


def step_plot_sed(params):
    """Plot SED dispersion and optional q-slice."""
    if not _plot_data_ready(params):
        print("  ⚠  Missing SED data — run compute first")
        return

    print("  ▶  Plotting SED ...")
    data = FileIO.load_data(params)
    Plot_SED.plot_bands(data, params)

    if params.plot_slice:
        Plot_SED.plot_slice(data, params)

    print("  ✓  Plot done")


def step_fit_sed(params):
    """Lorentzian fitting of SED peaks."""
    if not params.lorentz:
        print("  -  lorentz = 0 — skipping fit")
        return

    if not _plot_data_ready(params):
        print("  ⚠  Missing SED data — run compute first")
        return

    if params.lorentz_fit_all_qpoint:
        # plot first (needed for fitting context)
        if not _fit_ready(params):
            print("  ▶  Lorentz fitting all Q-points ...")
            data = FileIO.load_data(params)
            for j in range(len(data.q_distances)):
                params.qpoint_slice_index = j
                params.if_show_figures = False
                params.plot_lorentz = False
                data_reload = FileIO.load_data(params)
                Lorentz.lorentz(data_reload, params)

            FileIO.deal_total_fre_lifetime(params, len(data.q_distances))
            print("  ✓  Lorentz fit done → TOTAL-LORENTZ-Qpoints.Fre_lifetime")
        else:
            print("  ✓  TOTAL-LORENTZ-Qpoints.Fre_lifetime already exists — skipping fit")
    else:
        # single Q-point fit
        print(f"  ▶  Lorentz fitting Q-point #{params.qpoint_slice_index} ...")
        data = FileIO.load_data(params)
        Lorentz.lorentz(data, params)
        print("  ✓  Single Lorentz fit done")


def step_compute_dsf(params):
    """Compute dynamic structure factor."""
    if _dsf_ready(params):
        print(f"  ✓  {params.out_files_name}.dsf  already exists — skipping compute")
        return

    print("  ▶  Computing DSF ...")
    t0 = time.perf_counter()
    from mdtrace.dsf import compute_dsf, save_dsf
    result = compute_dsf(params)
    save_dsf(result, params)
    elapsed = time.perf_counter() - t0
    print(f"  ✓  DSF compute done ({elapsed:.1f} s)")


def step_plot_dsf(params):
    """Plot S(Q,ω) heatmap."""
    if not _dsf_ready(params):
        print("  ⚠  Missing .dsf data — run compute first")
        return

    print("  ▶  Plotting S(Q,ω) ...")
    # TODO: DSF plotter
    print("  ✓  Plot done (placeholder — DSF plotter coming in next step)")


def step_compute_eels(params):
    """Report the status of the planned EELS method."""

    print("  ERROR: EELS calculation is not implemented yet.")
    sys.exit(1)


# ── step registry ───────────────────────────────────────────────

STEP_MAP = {
    "sed": {
        "compute":  step_compute_sed,
        "plot":     step_plot_sed,
        "fit":      step_fit_sed,
    },
    "dsf": {
        "compute":  step_compute_dsf,
        "plot":     step_plot_dsf,
    },
    "eels": {
        "compute":  step_compute_eels,
    },
}


# ── pipeline ────────────────────────────────────────────────────

def run(params):
    """Execute the requested action for the given method."""

    method = getattr(params, "method", "sed")
    action = getattr(params, "action", "thinking")

    if method not in STEP_MAP:
        print(f"✖  Unknown method: '{method}'. Supported: {list(STEP_MAP.keys())}")
        sys.exit(1)

    steps = STEP_MAP[method]
    if action not in steps and action != "thinking":
        print(f"✖  Unknown action: '{action}'. Supported: thinking, {list(steps.keys())}")
        sys.exit(1)

    if method == "eels":
        step_compute_eels(params)

    if action in {"thinking", "compute"}:
        step_prepare_trajectory(params)

    if action == "thinking":
        # ── thinking mode: detect what needs doing ──
        _run_thinking(params, method, steps)
    else:
        # ── explicit action ──
        steps[action](params)

    print("\n  ✅ MDtrace task finished successfully.\n")


def _run_thinking(params, method, steps):
    """Auto-detect progress and run the next needed step(s)."""

    if method == "sed":
        needs_compute  = not _sed_ready(params)
        needs_fit      = params.lorentz and not _fit_ready(params)

        if needs_compute:
            print("  💡 thinking: no .SED found → compute + plot")
            steps["compute"](params)
            steps["plot"](params)
            if params.lorentz:
                steps["fit"](params)
            return

        if needs_fit:
            print("  💡 thinking: lorentz fit needed → plot + fit")
            steps["plot"](params)
            steps["fit"](params)
            return

        # Everything done
        print("  ✅  All steps already complete!")
        print("      Trajectory, .SED, plot, and fit data all exist.")
        print("      To replot, use action = plot.")
        print("      To recompute or refit all Q points, first rename or")
        print("      remove the corresponding existing output files.")

    elif method == "dsf":
        needs_compute  = not _dsf_ready(params)

        if needs_compute:
            print("  💡 thinking: no .dsf found → compute + plot")
            steps["compute"](params)
            steps["plot"](params)
            return

        print("  ✅  All steps already complete!")
        print("      Trajectory, .dsf, and plot data all exist.")
        print("      To replot, use action = plot.")
        print("      To recompute, first rename or remove the existing")
        print("      .dsf output file, then use action = compute.")
