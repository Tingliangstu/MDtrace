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

import os
from pylab import *
import seaborn as sns
import numpy as np

# *************************** Set Seaborn style for good look*************************
sns.set(style="ticks")
# Customize axis line, tick, and label properties
sns.set_context("paper", rc={"axes.linewidth": 0.75, "xtick.major.width": 0.75, "ytick.major.width": 0.75,
                             "axes.labelsize": 16, "xtick.labelsize": 13.5, "ytick.labelsize": 13.5})
# *************************** Set Seaborn style *************************

def _resolve_color_limits(sed, params):
    """Return natural-log color limits for SED values in eV/THz."""

    values = np.asarray(sed)
    positive = values[np.isfinite(values) & (values > 0)]
    if positive.size == 0:
        raise ValueError("SED data contain no positive values to plot")

    log_values = np.log(positive)
    automatic_min = np.trunc(log_values.min())
    automatic_max = np.trunc(log_values.max())
    if np.isclose(automatic_min, automatic_max):
        automatic_min -= 1.0
        automatic_max += 1.0

    vmin = (
        params.colorbar_min
        if params.colorbar_min is not None
        else automatic_min
    )
    vmax = (
        params.colorbar_max
        if params.colorbar_max is not None
        else automatic_max
    )
    if vmin >= vmax:
        raise ValueError(
            "resolved colorbar_min must be smaller than colorbar_max"
        )
    return vmin, vmax


def _prepare_sed_for_log_scale(sed, vmin, vmax):
    """Take the natural log of positive SED values and clip for rendering."""

    values = np.asarray(sed)
    positive = np.ma.masked_less_equal(values, 0.0)
    finite = np.ma.masked_invalid(positive)
    return np.ma.clip(np.ma.log(finite), vmin, vmax)


def _print_plot_detail(label, value):
    """Print one plot detail using the pipeline's column alignment."""

    print(f"      {label:<16}: {value}")


def _input_filename(params):
    """Return the actual input filename for user-facing plot guidance."""

    return os.path.basename(getattr(params, "input_file", "input.in"))


def _print_color_scale(params, vmin, vmax):
    """Print the resolved color scale in aligned, readable rows."""

    min_source = "user-defined" if params.colorbar_min is not None else "automatic"
    max_source = "user-defined" if params.colorbar_max is not None else "automatic"
    input_name = _input_filename(params)
    _print_plot_detail(
        "Colorbar",
        "ln[SED / (eV/THz)] (dimensionless)",
    )
    _print_plot_detail(
        "colorbar_min",
        f"{vmin:.6g} ({min_source}, ln scale)",
    )
    _print_plot_detail(
        "colorbar_max",
        f"{vmax:.6g} ({max_source}, ln scale)",
    )
    _print_plot_detail(
        "Fine-tune with",
        f"colorbar_min / colorbar_max in {input_name}",
    )


def resolve_slice_frequency_limit(thz, params):
    """Return the displayed upper frequency and its input control."""

    lorentz_freq_max = getattr(params, 'lorentz_fit_freq_max', None)
    if (
        getattr(params, 'plot_lorentz', False)
        and lorentz_freq_max is not None
    ):
        return lorentz_freq_max, "lorentz_fit_freq_max"
    plot_cutoff = getattr(params, 'plot_cutoff_freq', None)
    if plot_cutoff is not None:
        return plot_cutoff, "plot_cutoff_freq"
    return float(np.max(thz)), None


def resolve_slice_frequency_start(thz, params):
    """Return the displayed lower frequency and its input control."""

    lorentz_freq_min = getattr(params, 'lorentz_fit_freq_min', None)
    if (
        getattr(params, 'plot_lorentz', False)
        and lorentz_freq_min is not None
    ):
        return lorentz_freq_min, "lorentz_fit_freq_min"
    return float(np.min(thz)), None


def resolve_slice_output_path(params, lorentz=False):
    """Return the output path for one single-q SED figure."""

    q_index = params.qpoint_slice_index
    if getattr(params, 'plot_partial_SED', False):
        element = params.plot_partial_element
        direction = params.plot_partial_dir or "xyz"
        prefix = "LORENTZ-fitting-" if lorentz else ""
        filename = (
            f"{prefix}SED_{element}_{direction}-{q_index}-qpoint.png"
        )
        return os.path.join(
            params.out_files_name + '_partial_SED',
            filename,
        )
    if lorentz:
        return f"LORENTZ-fitting-{q_index}-qpoint.png"
    return f"SED-{q_index}-qpoint.png"


def plot_bands(data, params):
    # Get data
    sed_avg = data.sed_avg
    qpoints = data.qpoints
    thz = data.freq_fft
    q_distances = data.q_distances
    q_labels = data.q_labels
    
    # ******************** Control plotting params ********************
    color = params.plot_color               # 'inferno', 'RdBu_r', 'jet', 'Spectral', 'RdYlGn' (https://matplotlib.org/stable/tutorials/colors/colormaps.html)
    interp = 'hanning'                      # 'hanning'
    df = params.plot_interval               # Scale interval for drawing

    # For plot scale
    max_thz = max(thz)
    max_sed_y = np.size(sed_avg, 0)
    scale_factor = max_sed_y / max_thz
    
    vmin, vmax = _resolve_color_limits(sed_avg, params)
    sed_for_plot = _prepare_sed_for_log_scale(sed_avg, vmin, vmax)
    
    # ************************ Creat a figure, set its size *********************

    fig, ax = plt.subplots()
    fig.set_size_inches(5.5+(params.num_qpaths/2-0.5), 5)  # Control the size of the output image

    _print_color_scale(params, vmin, vmax)

    """
    Choose the plotting method based on the number of qpaths
    Set yticks (This part of the code is redundant, maybe I will remove the params.num_qpaths == 1, for now just to better repeat the previous results.)
    """
    if params.num_qpaths > 1 or params.use_contourf:
        levels = np.linspace(vmin, vmax, 350)
    	  
        im = ax.contourf(
            q_distances,
            thz,
            sed_for_plot,
            cmap=color,
            levels=levels,
            vmin=vmin,
            vmax=vmax,
        )
        
        # Draw vertical grey lines for q_labels (excluding endpoints)
        keys = list(q_labels.keys())
        for x in keys[1:-1]:            # Exclude first and last points
            ax.axvline(x, color='grey', linestyle='--', linewidth=0.8)

    else:
        _print_plot_detail(
            "Rendering",
            "SED is rendered with imshow; set "
            f"use_contourf = 1 in {_input_filename(params)} "
            "to use contourf",
        )
        im = ax.imshow(
            sed_for_plot,
            cmap=color,
            interpolation=interp,
            aspect='auto',
            origin='lower',
            vmin=vmin,
            vmax=vmax,
        )

    # colarbar
    bar = fig.colorbar(im, ax=ax)
    ticks = np.arange(vmin, vmax + 0.01, 2.0)
    if ticks.size >= 2:
        bar.set_ticks(ticks)
        bar.set_ticklabels([f"{tick:g}" for tick in ticks])
    bar.outline.set_visible(False)
    bar.ax.tick_params(labelsize=8, width=0, length=0, pad=0.6)
    bar.set_label(
        r'$\ln\!\left[\mathrm{SED}(\mathbf{q},\omega)'
        r'/(\mathrm{eV/THz})\right]$',
        fontsize=13.5,
    )

    # Set xticks and xticklabels
    if params.num_qpaths > 1 or params.use_contourf:
        xticks = list(q_labels.keys())

    else:
        ax.set_xlim([0, len(qpoints)-1])
        xticks = [0, len(qpoints)-1]

    xticklabels = [r'$\Gamma$' if label == 'G' else label for label in q_labels.values()]  # Replace 'G' with '$\Gamma$'
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, fontsize=16)

    """
    Set yticks (This part of the code is redundant, maybe I will remove the params.num_qpaths == 1,
     for now just to better repeat the previous results.)
    """
    if params.num_qpaths > 1 or params.use_contourf:
        max_freq = params.plot_cutoff_freq if params.plot_cutoff_freq else thz.max()
        num_ticks = int(np.ceil(max_freq / df)) + 1
        freqs = np.linspace(0, max_freq, num_ticks)

        ax.set_yticks(freqs)
        yticks_labels = [f'{f:.1f}'.rstrip('0').rstrip('.') for f in freqs]
        ax.set_yticklabels(yticks_labels, fontsize=13.5)
        ax.set_ylim([0, max_freq])

    else:
        freqs = np.arange(0, np.ceil(thz.max()) + 0.01, df)
        ids = np.zeros(len(freqs))
        for i in range(len(ids)):
            ids[i] = np.argwhere(thz <= freqs[i]).max()

        ax.set_yticks(ids)
        yticks_labels = [f'{f:.1f}'.rstrip('0').rstrip('.') for f in freqs]
        ax.set_yticklabels(yticks_labels, fontsize=13.5)

        # ax.set_ylim()
        if params.plot_cutoff_freq:
            ax.set_ylim([0, params.plot_cutoff_freq * scale_factor])

    ax.set_ylabel('Frequency (THz)', fontsize=16)

    if getattr(params, 'plot_partial_SED', 0):
        partial_dir = params.out_files_name + '_partial_SED'
        os.makedirs(partial_dir, exist_ok=True)
        element = params.plot_partial_element
        dir_label = params.plot_partial_dir if params.plot_partial_dir else "xyz"
        out_name = f"SED_{element}_{dir_label}.png"
        plt.savefig(os.path.join(partial_dir, out_name), format='png', dpi=650, bbox_inches='tight')
    else:
        plt.savefig('{}-SED.png'.format(params.out_files_name), format='png', dpi=650, bbox_inches='tight')

    if params.if_show_figures:
        plt.show()

def lorentzian(xarr, center, amplitude, hwhm):
    return amplitude / (1 + ((xarr - center) / hwhm) ** 2)

def plot_slice(data, params):
    # ******************** Get data ********************
    sed_avg = data.sed_avg
    qpoints = data.qpoints
    thz = data.freq_fft
    q_index = params.qpoint_slice_index
    
    ### ******************** creat a figure, set its size ********************
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 4)

    # ******************** For saving different files ********************
    save_flag = False
    # Plot
    alpha = 0.6

    ax.semilogy(
        thz,
        sed_avg[:, q_index],
        ls='-',
        lw=1.4,
        color="#aa3474",
        marker='o',
        ms=5.5,
        fillstyle='full',
        alpha=alpha,
        zorder=5,
    )

    # A standalone q-point slice does not have Lorentz-fit state.  The
    # fitting workflow adds this runtime-only flag before requesting an
    # overlay, so default to the original plain-SED behavior when absent.
    if getattr(params, 'plot_lorentz', False):
        save_flag = True
        fit_clusters = getattr(params, 'lorentz_fit_clusters', None)
        if fit_clusters is not None:
            selected_functions = {
                cluster.get('fitting_function', 'lorentz')
                for cluster in fit_clusters
            }
            if selected_functions == {'lorentz'}:
                component_name = 'Lorentz peaks (above baseline)'
            elif selected_functions == {'dho'}:
                component_name = 'DHO peaks (above baseline)'
            else:
                component_name = 'Peak components (above baseline)'
            component_label = True
            baseline_label = True
            fit_label = True
            for cluster in fit_clusters:
                fit_frequency = np.asarray(cluster['frequency'])
                physical = fit_frequency >= 0.0
                fit_frequency = fit_frequency[physical]

                components = [
                    np.asarray(component)[physical]
                    for component in cluster['component_curves']
                ]
                baseline = np.asarray(cluster['baseline_curve'])[physical]
                positive_baseline = baseline > 0.0
                has_visible_baseline = np.any(positive_baseline)
                predicted = np.asarray(cluster['predicted'])[physical]

                # For a zero-baseline single-peak window, the component and
                # total are identical. Plot only the component so the later
                # grey dashed curve cannot hide the green peak.
                total_is_duplicate = (
                    not has_visible_baseline and len(components) == 1
                )
                if not total_is_duplicate:
                    ax.semilogy(
                        fit_frequency,
                        predicted,
                        ls='--',
                        lw=1.8,
                        color='grey',
                        alpha=alpha + 0.2,
                        label='Fitted total' if fit_label else None,
                        zorder=2,
                    )
                    fit_label = False

                if has_visible_baseline:
                    ax.semilogy(
                        fit_frequency[positive_baseline],
                        baseline[positive_baseline],
                        ls=':',
                        lw=1.7,
                        color='C1',
                        alpha=alpha + 0.1,
                        label='Fitted baseline' if baseline_label else None,
                        zorder=3,
                    )
                    baseline_label = False

                for component in components:
                    ax.semilogy(
                        fit_frequency,
                        component,
                        ls='-',
                        lw=1.7,
                        color='C2',
                        alpha=alpha + 0.1,
                        label=component_name if component_label else None,
                        zorder=4,
                    )
                    component_label = False
            if fit_clusters:
                handles, labels = ax.get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                preferred_order = (
                    component_name,
                    'Fitted baseline',
                    'Fitted total',
                )
                ordered_labels = [
                    label for label in preferred_order if label in by_label
                ]
                ax.legend(
                    [by_label[label] for label in ordered_labels],
                    ordered_labels,
                    fontsize=11,
                    frameon=False,
                    handlelength=2.8,
                    labelspacing=0.6,
                )
        else:
            # Backward-compatible overlay for callers that only provide popt.
            total = np.zeros(len(sed_avg[:, q_index]))
            for i in range(len(params.popt[:, 0])):
                if params.popt[i, 2] == 0:
                    continue
                component = lorentzian(
                    thz,
                    params.popt[i, 0],
                    params.popt[i, 1],
                    params.popt[i, 2],
                )
                ax.semilogy(
                    thz,
                    component,
                    ls='-',
                    lw=1.5,
                    color='C2',
                    alpha=alpha,
                )
                total = total + component

            ax.semilogy(
                thz,
                total,
                ls='--',
                lw=1.5,
                color='grey',
                alpha=alpha + 0.2,
            )

    # ******************** set the figure labels ********************
    ax.set_ylabel(
        r'$\Phi(\mathbf{q},\omega)$ (eV/THz)'
    )
    ax.set_xlabel('Frequency (THz)')
    fig.suptitle(r'$\mathbf{{q}}$ = ({0:.3f}, {1:.3f}, {2:.3f})'.format(qpoints[q_index, 0], qpoints[q_index, 1],
                                                               qpoints[q_index, 2]), y=0.95, fontsize=15)

    min_frequency, _ = resolve_slice_frequency_start(thz, params)
    max_frequency, _ = resolve_slice_frequency_limit(thz, params)
    ax.set_xlim([min_frequency, max_frequency])

    if getattr(params, 'plot_partial_SED', 0):
        partial_dir = params.out_files_name + '_partial_SED'
        os.makedirs(partial_dir, exist_ok=True)
    output_path = resolve_slice_output_path(params, lorentz=save_flag)
    plt.savefig(
        output_path,
        format='png',
        dpi=650,
        bbox_inches='tight',
    )

    if params.if_show_figures:
        plt.show()

    plt.close(fig)
