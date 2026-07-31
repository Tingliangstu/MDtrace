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
import numpy as np


SED_HEADER = (
    "MDtrace spectral energy density; unit: eV/THz; "
    "each column corresponds to one q-point "
    "(same order as the .Qpts file)"
)

def _partial_sed_path(params, element, direction):
    """Return the element-labelled path for one Cartesian component."""

    partial_dir = params.out_files_name + '_partial_SED'
    output_name = os.path.basename(
        os.path.normpath(params.out_files_name)
    )
    filename = (
        f"{output_name}.SED_{element}_{direction}"
    )
    return os.path.join(partial_dir, filename)


def write_output(phonons, params, BZ_lattice_info):
    output_partial = getattr(params, 'output_partial', 0)
    if output_partial:
        # Overall SED = sum over element and direction.
        sed_total = phonons.sed_avg.sum(axis=(-2, -1))
        np.savetxt(
            params.out_files_name + '.SED',
            sed_total,
            header=SED_HEADER,
        )

        partial_dir = params.out_files_name + '_partial_SED'
        os.makedirs(partial_dir, exist_ok=True)
        dir_labels = ['x', 'y', 'z']
        output_name = os.path.basename(
            os.path.normpath(params.out_files_name)
        )

        for t_idx, element in enumerate(phonons.type_symbols):
            for d_idx, d_lab in enumerate(dir_labels):
                # Remove only the corresponding pre-1.0 type-labelled file.
                legacy_path = os.path.join(
                    partial_dir,
                    f"{output_name}.SED_type{t_idx + 1}_{d_lab}",
                )
                if os.path.isfile(legacy_path):
                    os.remove(legacy_path)

                out_path = _partial_sed_path(
                    params,
                    element,
                    d_lab,
                )
                np.savetxt(
                    out_path,
                    phonons.sed_avg[:, :, t_idx, d_idx],
                    header=SED_HEADER,
                )
    else:
        np.savetxt(
            params.out_files_name + '.SED',
            phonons.sed_avg,
            header=SED_HEADER,
        )

    np.savetxt(params.out_files_name + '.Qpts', BZ_lattice_info.reduced_qpoints, fmt='%.8f')
    np.savetxt(params.out_files_name + '.THz', phonons.freq_fft, fmt='%.8f')

    with open(params.out_files_name + '.Q_distances_and_labels', 'w') as f:
        # q_distances
        f.write("Global distances along the paths:\n")
        f.write(" ".join(f"{d:.10f}" for d in BZ_lattice_info.q_distances) + "\n\n")

        # q_labels
        f.write("High-symmetry points and their distances:\n")
        for distance, label in BZ_lattice_info.q_labels:
            f.write(f"{float(distance):.10f}   {label}\n")

class load_data(object):

    def __init__(self, params):

        if getattr(params, 'plot_partial_SED', 0):

            element = params.plot_partial_element

            if params.plot_partial_dir is None:
                # Sum x/y/z for the requested element.
                file_x = _partial_sed_path(params, element, 'x')
                file_y = _partial_sed_path(params, element, 'y')
                file_z = _partial_sed_path(params, element, 'z')
                if not all(
                    os.path.exists(path)
                    for path in (file_x, file_y, file_z)
                ):
                    raise FileNotFoundError(
                        f"partial SED files for element '{element}' are missing")
                sed_x = np.loadtxt(file_x)
                sed_y = np.loadtxt(file_y)
                sed_z = np.loadtxt(file_z)
                self.sed_avg = sed_x + sed_y + sed_z
            else:
                d = params.plot_partial_dir
                file_d = _partial_sed_path(params, element, d)
                if not os.path.exists(file_d):
                    raise FileNotFoundError(
                        f"partial SED file for element '{element}' "
                        f"and direction '{d}' is missing")
                self.sed_avg = np.loadtxt(file_d)

        else:
            self.sed_avg = np.loadtxt(params.out_files_name + '.SED')

        self.qpoints = np.loadtxt(params.out_files_name + '.Qpts')
        self.freq_fft = np.loadtxt(params.out_files_name + '.THz')

        self.q_distances = []
        self.q_labels = {}
        with open(params.out_files_name + '.Q_distances_and_labels', 'r') as f:
            lines = f.readlines()
            # q_distances
            if lines[0].strip() == "Global distances along the paths:":
                self.q_distances = [float(x) for x in lines[1].split()]
            # q_labels
            if lines[3].strip() == "High-symmetry points and their distances:":
                for line in lines[4:]:
                    distance, label = line.split(maxsplit=1)
                    self.q_labels[float(distance)] = label.strip()

def write_lorentz(lorentz, params):
    prefix = (
        params.out_files_name
        + '_LORENTZ-{}'.format(params.qpoint_slice_index)
    )
    parameter_file = prefix + '.params'
    error_file = prefix + '.error'
    baseline_file = prefix + '.baseline'
    model_file = prefix + '.models'
    np.savetxt(
        parameter_file,
        lorentz.popt,
        header='center_THz amplitude_eV_per_THz hwhm_THz',
    )
    np.savetxt(
        error_file,
        lorentz.pcov,
        header='center_error_THz amplitude_error_eV_per_THz hwhm_error_THz',
    )

    with open(baseline_file, 'w', encoding='utf-8') as stream:
        stream.write(
            '# cluster model fit_min_THz fit_max_THz '
            'B0_eV_per_THz slope_eV_per_THz2 AICc RSS '
            'strategy fitting_function num_points\n'
        )
        for cluster_number, result in enumerate(
            getattr(lorentz, 'fit_clusters', []),
            start=1,
        ):
            b0, slope = result['baseline_parameters']
            stream.write(
                f"{cluster_number:d} {result['baseline_model']} "
                f"{result['fit_start']:.10g} {result['fit_end']:.10g} "
                f"{b0:.10g} {slope:.10g} {result['aicc']:.10g} "
                f"{result['rss']:.10g} "
                f"{result.get('peak_strategy', 'joint')} "
                f"{result.get('fitting_function', 'lorentz')} "
                f"{result.get('num_points', len(result['frequency']))}\n"
            )

    with open(model_file, 'w', encoding='utf-8') as stream:
        stream.write(
            '# peak model strategy peak_significance damping_ratio regime '
            'damped_frequency_THz slow_relaxation_ps fast_relaxation_ps '
            'width_at_upper_bound unresolved_width\n'
        )
        models = getattr(
            lorentz,
            'fit_models',
            np.full(len(lorentz.popt), 'lorentz', dtype=object),
        )
        strategies = getattr(
            lorentz,
            'fit_strategies',
            np.full(len(lorentz.popt), 'independent', dtype=object),
        )
        upper_hits = getattr(
            lorentz,
            'upper_bound_hits',
            np.zeros(len(lorentz.popt), dtype=bool),
        )
        unresolved = getattr(
            lorentz,
            'unresolved_widths',
            np.zeros(len(lorentz.popt), dtype=bool),
        )
        significance = getattr(
            lorentz,
            'peak_significance',
            np.full(len(lorentz.popt), np.nan, dtype=float),
        )
        for peak_number, (
            parameters,
            model,
            strategy,
            peak_significance,
            upper_hit,
            unresolved_width,
        ) in enumerate(
            zip(
                lorentz.popt,
                models,
                strategies,
                significance,
                upper_hits,
                unresolved,
            ),
            start=1,
        ):
            center, _, hwhm = parameters
            if model == 'dho' and center > 0.0:
                damping_ratio = hwhm / center
                if np.isclose(damping_ratio, 1.0, rtol=1.0e-6):
                    regime = 'critical'
                    damped_frequency = 0.0
                    slow_relaxation = 1.0 / (2.0 * np.pi * hwhm)
                    fast_relaxation = slow_relaxation
                elif damping_ratio < 1.0:
                    regime = 'underdamped'
                    damped_frequency = np.sqrt(center**2 - hwhm**2)
                    slow_relaxation = np.nan
                    fast_relaxation = np.nan
                else:
                    regime = 'overdamped'
                    damped_frequency = 0.0
                    root = np.sqrt(hwhm**2 - center**2)
                    slow_relaxation = 1.0 / (
                        2.0 * np.pi * (hwhm - root)
                    )
                    fast_relaxation = 1.0 / (
                        2.0 * np.pi * (hwhm + root)
                    )
            else:
                damping_ratio = np.nan
                regime = 'not_applicable'
                damped_frequency = np.nan
                slow_relaxation = np.nan
                fast_relaxation = np.nan
            stream.write(
                f"{peak_number:d} {model} {strategy} "
                f"{peak_significance:.10g} "
                f"{damping_ratio:.10g} {regime} "
                f"{damped_frequency:.10g} {slow_relaxation:.10g} "
                f"{fast_relaxation:.10g} {int(upper_hit)} "
                f"{int(unresolved_width)}\n"
            )
    return parameter_file, error_file, baseline_file, model_file


def hwhm_to_lifetime_ps(hwhm):
    """Convert ordinary-frequency HWHM in THz to lifetime in ps."""

    hwhm = np.asarray(hwhm, dtype=float)
    lifetime = np.full(hwhm.shape, np.nan, dtype=float)
    valid = np.isfinite(hwhm) & (hwhm > 0)
    lifetime[valid] = 1.0 / (2.0 * np.pi * hwhm[valid])
    return lifetime


def write_phonon_lifetime(lorentz, params):

    out_lifetime_file = 'Generated by mdtrace, Email: liangting.zj@gmail.com\n'
    out_lifetime_file += (
        "First_line: Frequency (THz)  Second_line: Phonon Lifetime (ps); "
        "overdamped DHO fits are omitted and recorded in the .models file\n"
    )

    lifetimes = hwhm_to_lifetime_ps(lorentz.popt[:, 2])
    models = getattr(
        lorentz,
        'fit_models',
        np.full(len(lorentz.popt), 'lorentz', dtype=object),
    )
    for fit_parameters, lifetime, model in zip(
        lorentz.popt,
        lifetimes,
        models,
    ):
        if not np.isfinite(lifetime):  # don't output failed fits
            continue
        if model == 'dho' and fit_parameters[2] >= fit_parameters[0]:
            continue

        # TODO: Decide how lifetime should be named and reported; see TODO.md.
        # The current 1/(2*pi*HWHM_f) is the amplitude/coherence lifetime T2,
        # as used by dynasor. The energy-relaxation lifetime T1 used in phonon
        # transport is 1/(4*pi*HWHM_f) when pure dephasing is negligible.
        # Consider reporting the fitted linewidth plus explicitly labelled T1/T2.
        out_lifetime_file += '{0:.6f} {1:.8f} \n'.format(
            fit_parameters[0],
            lifetime,
        )
        # write the file

    output_file = 'LORENTZ-{}-th-Qpoints.Fre_lifetime'.format(
        params.qpoint_slice_index
    )
    f = open(output_file, 'w')
    f.write(out_lifetime_file)
    f.close()
    return output_file

def deal_total_fre_lifetime(params, total_qpoints):

    out_lifetime_file = 'Generated by mdtrace, Email: liangting.zj@gmail.com\n'
    out_lifetime_file += "First_line: Frequency (THz)  Second_line: Phonon Lifetime (ps)\n"

    total_num_Fre_lifetime = 0

    for i in range(total_qpoints):
        load_file_name = 'LORENTZ-{}-th-Qpoints.Fre_lifetime'.format(i)
        try:
            with open(load_file_name, 'r') as f:
                lines = [line.strip() for line in f.readlines()]
                # Check if the file only contains the header lines
                if len(lines) <= 2 or all(line == '' for line in lines[2:]):
                    print(f'\nWarning: {load_file_name} does not contain fitted phonon lifetimes, skipping.')
                    continue

            # Load the numerical data
            Freq, lifetime = np.loadtxt(load_file_name, skiprows=2, unpack=True)

            if isinstance(Freq, np.float64):
                Freq = np.array([Freq])
                lifetime = np.array([lifetime])

            for j in range(len(Freq)):
                out_lifetime_file += '{0:.6f} {1:.8f}\n'.format(Freq[j], lifetime[j])
                total_num_Fre_lifetime += 1

        except:
            raise FileNotFoundError(
                '\n*************** File LORENTZ-{}-th-Qpoints.Fre_lifetime reading ERROR ***************'.format(i))

    output_file = 'TOTAL-LORENTZ-Qpoints.Fre_lifetime'
    f = open(output_file, 'w')
    f.write(out_lifetime_file)
    f.close()
    return output_file, total_num_Fre_lifetime
