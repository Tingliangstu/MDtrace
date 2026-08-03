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

from mdtrace.io.netcdf import is_netcdf
from mdtrace.io.prepare import prepare_trajectory
from mdtrace.io.schema import CELLS
from mdtrace.io.trajectory import prefetch_one, trajectory_block_source
from mdtrace.parameters import validate_qpoint_slice_index
from mdtrace.sed import (
    FileIO,
    Lorentz,
    OutputPaths,
    Phonon,
    Plot_SED,
    construct_BZ,
)

_FIT_BLOCK_SEPARATOR = "  " + "-" * 58

# ── step detectors ──────────────────────────────────────────────

def _sed_ready(params):
    return os.path.exists(params.out_files_name + ".SED")


def _qpts_ready(params):
    return os.path.exists(params.out_files_name + ".Qpts")


def _thz_ready(params):
    return os.path.exists(params.out_files_name + ".THz")


def _plot_data_ready(params):
    return _sed_ready(params) and _qpts_ready(params) and _thz_ready(params)


def _dispersion_plot_path(params):
    """Return the dispersion image produced by the current plot selection."""

    if getattr(params, "plot_partial_SED", False):
        direction = params.plot_partial_dir or "xyz"
        return (
            Path(params.out_files_name + "_partial_SED")
            / f"SED_{params.plot_partial_element}_{direction}.png"
        )
    return Path(params.out_files_name + "-SED.png")


def _slice_plot_path(params):
    """Return the plain single-q image produced by the plot action."""

    q_index = params.qpoint_slice_index
    if getattr(params, "plot_partial_SED", False):
        direction = params.plot_partial_dir or "xyz"
        return (
            Path(params.out_files_name + "_partial_SED")
            / (
                f"SED_{params.plot_partial_element}_{direction}-"
                f"{q_index}-qpoint.png"
            )
        )
    return Path(f"SED-{q_index}-qpoint.png")


def _plot_ready(params):
    """Return whether the images requested by the current input exist."""

    if not _dispersion_plot_path(params).is_file():
        return False
    return (
        not getattr(params, "plot_slice", False)
        or _slice_plot_path(params).is_file()
    )


def _fit_ready(params):
    """Return whether the currently requested fit output exists."""

    if params.lorentz_fit_all_qpoint:
        output = OutputPaths.combined_lifetime_data()
    else:
        output = OutputPaths.qpoint_lifetime_data(
            params.qpoint_slice_index
        )
    return output.is_file()


def _print_detail(label, value):
    """Print one aligned detail row for the current pipeline step."""

    print(f"      {label:<16}: {value}")


def _sed_component_description(params):
    """Describe the total or partial SED selected for plotting."""

    if not getattr(params, "plot_partial_SED", False):
        return "total SED"
    direction = params.plot_partial_dir or "x+y+z (summed)"
    return f"{params.plot_partial_element}, direction {direction}"


def _dsf_ready(params):
    return os.path.exists(params.out_files_name + ".dsf")


# ── step runners ────────────────────────────────────────────────

def step_prepare_trajectory(params):
    """Resolve a text trajectory to direct reading or a NetCDF cache."""
    source = Path(params.trajectory_file)
    input_directory = Path(params.input_file).parent
    converted_path = input_directory / f"{source.name}.mdtrace.nc"

    t0 = time.perf_counter()
    prepared, source_format = prepare_trajectory(
        source=source,
        converted_path=converted_path,
        lammps_unit=params.lammps_unit,
        batch_size=params.netcdf_batch_size,
        compression_level=params.netcdf_compression_level,
        text_mode=params.trajectory_read_mode,
    )
    params.source_format = source_format
    params.trajectory_path = str(prepared)
    elapsed = time.perf_counter() - t0
    if prepared == source and is_netcdf(prepared):
        print(f"  ✓  Reading NetCDF trajectory: {prepared}\n")
    elif prepared == source:
        print(f"  ✓  Reading text trajectory directly: {prepared}")
        print("      NetCDF cache         : disabled\n")
    else:
        print(f"  ✓  Trajectory ready: {prepared} ({elapsed:.1f} s)\n")


def step_compute_sed(params):
    """Compute phonon SED."""
    step_prepare_trajectory(params)
    print("  ▶  Computing phonon SED ...")
    t0 = time.perf_counter()

    trajectory = trajectory_block_source(params)
    num_frames = params.total_num_steps // params.output_data_stride
    block_size = num_frames // params.num_blocks
    raw_blocks = trajectory.iter_blocks(block_size, params.num_blocks)
    prefetch_enabled = bool(
        params.trajectory_prefetch and params.num_blocks > 1
    )
    if prefetch_enabled:
        prefetch_status = (
            "ON (next block loads in background; may speed up SED)"
        )
    elif params.trajectory_prefetch:
        prefetch_status = "OFF (only one block to process)"
    else:
        prefetch_status = "OFF (blocks load when needed)"
    print(f"      Trajectory prefetch : {prefetch_status}")
    with prefetch_one(raw_blocks, enabled=prefetch_enabled) as blocks:
        try:
            first_block = next(blocks)
        except StopIteration as error:
            raise EOFError("trajectory contains no readable frames") from error

        BZ_info = construct_BZ.BZ_methods(
            params,
            first_block.data[CELLS][0],
        )
        sed = Phonon.spectral_energy_density(params, trajectory.info)
        setup_done = time.perf_counter()
        sed.compute_sed(
            params,
            BZ_info,
            first_block,
            blocks,
        )
        calculation_done = time.perf_counter()

    # Some parallel workers may leave dangling imports; silence them
    sys.stdout.flush()

    FileIO.write_output(sed, params, BZ_info)
    finished = time.perf_counter()
    elapsed = finished - t0
    print(f"  ✓  SED compute done ({elapsed:.1f} s)")
    print(f"      Initial read/setup : {setup_done - t0:.1f} s")
    print(
        "      SED calculation    : "
        f"{calculation_done - setup_done:.1f} s"
    )
    print(
        "      Output/finalization: "
        f"{finished - calculation_done:.1f} s"
    )


def step_plot_sed(params):
    """Plot SED dispersion and optional q-slice."""
    if not _plot_data_ready(params):
        print("  ⚠  Missing SED data — run compute first")
        return

    data = FileIO.load_data(params)
    if params.plot_slice:
        validate_qpoint_slice_index(params, data.qpoints)

    print("  ▶  Plotting SED dispersion")
    _print_detail("Component", _sed_component_description(params))
    Plot_SED.plot_bands(data, params)

    if params.plot_slice:
        q_index = params.qpoint_slice_index
        qpoint = data.qpoints[q_index]
        max_frequency, frequency_control = (
            Plot_SED.resolve_slice_frequency_limit(data.freq_fft, params)
        )
        input_name = Path(
            getattr(params, "input_file", "input.in")
        ).name
        frequency_parameter = (
            frequency_control or "plot_cutoff_freq"
        )
        frequency_guidance = (
            f"adjust with {frequency_parameter} in {input_name}"
        )
        print("\n  ▶  Plotting single-q SED")
        _print_detail("q-point index", f"{q_index} (zero-based)")
        _print_detail(
            "q-point",
            f"({qpoint[0]:.6g}, {qpoint[1]:.6g}, {qpoint[2]:.6g})",
        )
        _print_detail(
            "Frequency range",
            f"0 to {max_frequency:g} THz ({frequency_guidance})",
        )
        _print_detail("Component", _sed_component_description(params))
        _print_detail(
            "Y-axis",
            "SED (eV/THz), logarithmic scale",
        )
        Plot_SED.plot_slice(data, params)

    print("\n  ✓  SED plotting complete")


def step_fit_sed(params):
    """Fit SED peaks and write linewidth-derived lifetimes."""
    if not _plot_data_ready(params):
        print("  ⚠  Missing SED data — run compute first")
        return

    if params.lorentz_fit_all_qpoint:
        # plot first (needed for fitting context)
        print("  ▶  Fitting spectral peaks at all Q-points ...")
        data = FileIO.load_data(params)
        total_qpoints = len(data.q_distances)
        incomplete_qpoints = []
        print(f"      Total Q-points       : {total_qpoints}")
        for j in range(total_qpoints):
            print(f"\n{_FIT_BLOCK_SEPARATOR}")
            print(
                f"  ▶  Fitting Q-point #{j} "
                f"({j + 1}/{total_qpoints}) ..."
            )
            params.qpoint_slice_index = j
            params.if_show_figures = False
            params.plot_lorentz = False
            data_reload = FileIO.load_data(params)
            fit_result = Lorentz.lorentz(data_reload, params)
            incomplete_peaks = [
                int(result["peak_number"])
                for result in fit_result.fit_clusters
                if result["incomplete_peak_shapes"][0]
            ]
            if incomplete_peaks:
                incomplete_qpoints.append((j, incomplete_peaks))

        total_file, total_modes = FileIO.deal_total_fre_lifetime(
            params,
            total_qpoints,
        )
        lifetime_figure = None
        if total_modes:
            frequency, lifetime = FileIO.read_lifetime_data(total_file)
            lifetime_figure = Plot_SED.plot_lifetime_summary(
                frequency,
                lifetime,
                params,
            )
            params.lifetime_figure_output = lifetime_figure
        print("\n  ▶  All-Q fitting summary")
        print(f"      {'Q-points processed':<20}: {total_qpoints}")
        print(f"      {'Fitted modes':<20}: {total_modes}")
        print(f"      {'Lifetime data':<20}: {total_file}")
        print(
            f"      {'Q-point figures':<20}: "
            f"{OutputPaths.FITTING_QPOINT_DIRECTORY}"
        )
        print("\n  ✓  All-Q spectral fitting complete")
        if incomplete_qpoints:
            incomplete_peak_count = sum(
                len(peaks) for _, peaks in incomplete_qpoints
            )
            peak_word = "peak" if incomplete_peak_count == 1 else "peaks"
            qpoint_word = (
                "Q-point" if len(incomplete_qpoints) == 1 else "Q-points"
            )
            print("\n  >  Q-points to inspect")
            print(
                "      Incomplete line shapes: "
                f"{incomplete_peak_count} {peak_word} across "
                f"{len(incomplete_qpoints)} {qpoint_word}"
            )
            for qpoint_index, peak_numbers in incomplete_qpoints:
                fitted_peak_word = (
                    "peak" if len(peak_numbers) == 1 else "peaks"
                )
                peak_list = ", ".join(str(number) for number in peak_numbers)
                print(
                    f"      Q-point #{qpoint_index:<8}: "
                    f"{fitted_peak_word} {peak_list}"
                )
            print("      Check these figures in Fitting-Qpoint/.")
            print("      Adjust peak_min_significance if needed.")
        print(
            "\n  Tip: Check all fit figures. To refine one Q point, set its"
        )
        print(
            "       qpoint_slice_index, adjust peak_min_significance and"
        )
        print(
            "       fitting_function = auto | lorentz | dho, then set"
        )
        print("       lorentz_fit_all_qpoint = 0 and")
        print("       re_output_total_freq_lifetime = 1.")
    else:
        # single Q-point fit
        print(f"  ▶  Fitting Q-point #{params.qpoint_slice_index} ...")
        data = FileIO.load_data(params)
        validate_qpoint_slice_index(params, data.qpoints)
        Lorentz.lorentz(data, params)
        if getattr(params, "re_output_total_freq_lifetime", False):
            total_file, total_modes = FileIO.deal_total_fre_lifetime(
                params,
                len(data.q_distances),
            )
            lifetime_figure = None
            if total_modes:
                frequency, lifetime = FileIO.read_lifetime_data(total_file)
                lifetime_figure = Plot_SED.plot_lifetime_summary(
                    frequency,
                    lifetime,
                    params,
                )
                params.lifetime_figure_output = lifetime_figure
                params.lifetime_figure_action = "redrawn"
            print(
                "  ✓  Combined lifetime data rebuilt → "
                f"{total_file} ({total_modes} modes)"
            )
        print("\n  ✓  Single-Q spectral fit done")


def step_compute_dsf(params):
    """Compute dynamic structure factor."""
    step_prepare_trajectory(params)
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

    params.lifetime_figure_output = None
    params.lifetime_figure_action = "written"
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

    if action == "thinking":
        # ── thinking mode: detect what needs doing ──
        _run_thinking(params, method, steps)
    else:
        # ── explicit action ──
        steps[action](params)

    lifetime_figure = getattr(params, "lifetime_figure_output", None)
    if lifetime_figure is not None:
        figure_action = getattr(
            params,
            "lifetime_figure_action",
            "written",
        )
        print(
            f"\n  🖼  Lifetime figure {figure_action}: {lifetime_figure}"
        )
    print("\n  ✅ MDtrace task finished successfully.\n")


def _run_thinking(params, method, steps):
    """Auto-detect progress and run the next needed step(s)."""

    if method == "sed":
        if not _plot_data_ready(params):
            print("  💡 thinking: incomplete SED data → compute + plot")
            steps["compute"](params)
            steps["plot"](params)
            return

        if not _plot_ready(params):
            print("  💡 thinking: SED data found, plot missing → plot")
            steps["plot"](params)
            return

        if not _fit_ready(params):
            print("  💡 thinking: SED data and plots ready → fit")
            steps["fit"](params)
            return

        # Everything done
        print("  ✅  All steps already complete!")
        print("      Trajectory, .SED, plot, and fit data all exist.")
        print("      To replot, use action = plot.")
        print("      To compute, use action = compute.")
        print("      To fit, use action = fit.")

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
