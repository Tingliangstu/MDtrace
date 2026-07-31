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

import numpy as np
from mdtrace.sed import FileIO, Plot_SED
from scipy.optimize import curve_fit
from scipy.signal import (
    find_peaks,
    peak_prominences,
    peak_widths,
    windows,
)


_PEAK_DETECTION_SMOOTH_WINDOW = 7
_PEAK_DETECTION_NOISE_WINDOW = 31
_MAD_TO_SIGMA = 1.4826
_BASELINE_MODELS = ("none", "constant", "linear")
_FITTING_FUNCTIONS = ("lorentz", "dho")
_AUTO_AICC_EQUIVALENCE = 2.0
_ADAPTIVE_HWHM_FACTOR = 4.0
_ADAPTIVE_HWHM_MIN_BINS = 5.0
_AUTO_OVERLAP_EXPANSION = 2.5
_JOINT_OVERLAP_EXPANSION = 4.0
_DHO_MIN_DISTINGUISHABLE_DAMPING_RATIO = 0.05


def _odd_window_length(size, requested):
    """Return the largest usable odd window, or one for very short data."""

    window_len = min(size, requested)
    if window_len % 2 == 0:
        window_len -= 1
    return max(window_len, 1)


def _hann_smooth(values, window_len=_PEAK_DETECTION_SMOOTH_WINDOW):
    """Return a detection-only Hann-smoothed copy of one spectrum."""

    values = np.asarray(values, dtype=float)
    window_len = _odd_window_length(values.size, window_len)
    if window_len < 3:
        return values.copy()

    window = windows.hann(window_len)
    pad = window_len // 2
    padded = np.pad(values, (pad, pad), mode="reflect")
    return np.convolve(padded, window / window.sum(), mode="valid")


def _rolling_mad(values, window_len=_PEAK_DETECTION_NOISE_WINDOW):
    """Return a rolling median absolute deviation with reflected edges."""

    values = np.asarray(values, dtype=float)
    window_len = _odd_window_length(values.size, window_len)
    if window_len < 3:
        return np.zeros_like(values)

    pad = window_len // 2
    padded = np.pad(values, (pad, pad), mode="reflect")
    local_windows = np.lib.stride_tricks.sliding_window_view(
        padded,
        window_len,
    )
    local_medians = np.median(local_windows, axis=1)
    return np.median(
        np.abs(local_windows - local_medians[:, np.newaxis]),
        axis=1,
    )


def _complete_peak_properties(sed, peaks, properties):
    """Ensure fitting properties use the original linear SED values."""

    properties = dict(properties)
    properties["peak_heights"] = sed[peaks]
    prominences, left_bases, right_bases = peak_prominences(sed, peaks)
    properties["prominences"] = prominences
    properties["left_bases"] = left_bases
    properties["right_bases"] = right_bases
    return properties


def _find_sed_peaks(
    sed,
    peak_min_significance=None,
    peak_height=None,
    peak_prominence=None,
):
    """Detect SED peaks and return linear-scale properties for fitting.

    When ``peak_min_significance`` is set, candidates are detected from a
    Hann-smoothed log spectrum using a local robust-noise prominence. The
    optional height and prominence values remain absolute filters on the
    original linear SED.
    """

    sed = np.asarray(sed, dtype=float)
    if peak_min_significance is None:
        peaks, properties = find_peaks(
            sed,
            height=peak_height,
            prominence=peak_prominence,
        )
        return peaks, _complete_peak_properties(sed, peaks, properties), None

    positive = sed[np.isfinite(sed) & (sed > 0)]
    if not positive.size:
        raise ValueError(
            "peak significance detection requires positive finite SED values"
        )

    log_floor = max(
        np.min(positive) * 1.0e-12,
        np.finfo(float).tiny,
    )
    log_sed = np.log(
        np.where(np.isfinite(sed) & (sed > 0), sed, log_floor)
    )
    smooth_log_sed = _hann_smooth(log_sed)
    residual = log_sed - smooth_log_sed

    local_sigma = _MAD_TO_SIGMA * _rolling_mad(residual)
    residual_median = np.median(residual)
    global_sigma = _MAD_TO_SIGMA * np.median(
        np.abs(residual - residual_median)
    )
    sigma_floor = max(0.1 * global_sigma, np.finfo(float).eps)
    local_sigma = np.maximum(local_sigma, sigma_floor)

    minimum_prominence = peak_min_significance * local_sigma
    candidates, detection_properties = find_peaks(
        smooth_log_sed,
        prominence=minimum_prominence,
    )
    detection_significance = (
        detection_properties["prominences"] / local_sigma[candidates]
    )

    refinement_radius = _odd_window_length(
        sed.size,
        _PEAK_DETECTION_SMOOTH_WINDOW,
    ) // 2
    refined = {}
    for candidate, significance in zip(
        candidates,
        detection_significance,
    ):
        left = max(0, candidate - refinement_radius)
        right = min(sed.size, candidate + refinement_radius + 1)
        peak = left + int(np.argmax(sed[left:right]))
        if 0 < peak < sed.size - 1:
            refined[peak] = max(refined.get(peak, 0.0), significance)

    peaks = np.array(sorted(refined), dtype=int)
    significance = np.array(
        [refined[peak] for peak in peaks],
        dtype=float,
    )
    properties = _complete_peak_properties(sed, peaks, {})

    keep = np.ones(peaks.size, dtype=bool)
    if peak_height is not None:
        keep &= properties["peak_heights"] >= peak_height
    if peak_prominence is not None:
        keep &= properties["prominences"] >= peak_prominence

    peaks = peaks[keep]
    significance = significance[keep]
    properties = {
        name: values[keep]
        for name, values in properties.items()
    }
    return peaks, properties, significance


def _select_lorentz_frequency_range(
    frequency,
    sed,
    freq_min=None,
    freq_max=None,
):
    """Select the inclusive frequency interval used for fitting."""

    frequency = np.asarray(frequency)
    sed = np.asarray(sed)
    mask = np.ones(frequency.shape, dtype=bool)
    if freq_min is not None:
        mask &= frequency >= freq_min
    if freq_max is not None:
        mask &= frequency <= freq_max
    if np.count_nonzero(mask) < 3:
        raise ValueError(
            "the requested Lorentz fitting frequency range contains "
            "fewer than three frequency samples"
        )
    return frequency[mask], sed[mask]


def _lorentzian(xarr, center, amplitude, hwhm):
    """Return one Lorentzian whose amplitude is measured above baseline."""

    return amplitude / (1.0 + ((xarr - center) / hwhm) ** 2)


def _velocity_dho(xarr, center, amplitude, hwhm):
    """Return a peak-normalized velocity-spectrum DHO line shape.

    ``hwhm`` is half of the DHO damping linewidth, so the DHO FWHM is
    ``2*hwhm`` and the weak-damping lifetime remains
    ``1/(2*pi*hwhm)``.  With this parameterization the peak value at
    ``xarr == center`` is ``amplitude``.
    """

    xarr = np.asarray(xarr, dtype=float)
    damping_width = 2.0 * hwhm
    numerator = amplitude * damping_width**2 * xarr**2
    denominator = (
        (xarr**2 - center**2) ** 2
        + damping_width**2 * xarr**2
    )
    result = np.zeros_like(xarr)
    np.divide(
        numerator,
        denominator,
        out=result,
        where=denominator > 0.0,
    )
    result[np.isclose(xarr, center) & np.isclose(denominator, 0.0)] = (
        amplitude
    )
    return result


def _line_shape_function(name):
    """Return the requested peak line-shape callable."""

    return {"lorentz": _lorentzian, "dho": _velocity_dho}[name]


def _baseline_parameter_count(model):
    """Return the number of free baseline parameters for *model*."""

    return {"none": 0, "constant": 1, "linear": 2}[model]


def _baseline_from_raw_parameters(xarr, model, raw_parameters, edges):
    """Evaluate a non-negative baseline parameterized at the fit edges."""

    xarr = np.asarray(xarr, dtype=float)
    if model == "none":
        return np.zeros_like(xarr)
    if model == "constant":
        return np.full_like(xarr, raw_parameters[0], dtype=float)

    left, right = edges
    if np.isclose(left, right):
        return np.full_like(xarr, raw_parameters[0], dtype=float)
    fraction = (xarr - left) / (right - left)
    return raw_parameters[0] + fraction * (
        raw_parameters[1] - raw_parameters[0]
    )


def _reported_baseline_parameters(model, raw_parameters, edges):
    """Return ``(B0, slope)`` at the center of a fitted interval."""

    if model == "none":
        return np.array([0.0, 0.0])
    if model == "constant":
        return np.array([raw_parameters[0], 0.0])

    left, right = edges
    slope = (raw_parameters[1] - raw_parameters[0]) / (right - left)
    return np.array(
        [0.5 * (raw_parameters[0] + raw_parameters[1]), slope]
    )


def _make_multi_peak_model(
    num_peaks,
    baseline_model,
    edges,
    fitting_function="lorentz",
):
    """Build a curve-fit callable for one peak cluster."""

    baseline_count = _baseline_parameter_count(baseline_model)
    peak_function = _line_shape_function(fitting_function)

    def model(xarr, *parameters):
        peak_parameters = np.asarray(
            parameters[: 3 * num_peaks],
            dtype=float,
        ).reshape(num_peaks, 3)
        total = np.zeros_like(np.asarray(xarr, dtype=float))
        for center, amplitude, hwhm in peak_parameters:
            total += peak_function(xarr, center, amplitude, hwhm)

        if baseline_count:
            raw_baseline = parameters[-baseline_count:]
            total += _baseline_from_raw_parameters(
                xarr,
                baseline_model,
                raw_baseline,
                edges,
            )
        return total

    return model


def _make_multi_lorentzian(num_peaks, baseline_model, edges):
    """Backward-compatible Lorentz-only model builder."""

    return _make_multi_peak_model(
        num_peaks,
        baseline_model,
        edges,
        fitting_function="lorentz",
    )


def _aicc(residuals, num_parameters):
    """Return the small-sample Akaike information criterion."""

    residuals = np.asarray(residuals, dtype=float)
    num_samples = residuals.size
    if num_samples <= num_parameters + 1:
        return np.inf

    rss = float(np.dot(residuals, residuals))
    mean_square = max(rss / num_samples, np.finfo(float).tiny)
    aic = num_samples * np.log(mean_square) + 2.0 * num_parameters
    correction = (
        2.0
        * num_parameters
        * (num_parameters + 1)
        / (num_samples - num_parameters - 1)
    )
    return aic + correction


def _initial_edge_baseline(sed):
    """Estimate the baseline at both edges of one fitting window."""

    sed = np.asarray(sed, dtype=float)
    edge_count = max(2, min(8, sed.size // 5))
    left = max(0.0, float(np.median(sed[:edge_count])))
    right = max(0.0, float(np.median(sed[-edge_count:])))
    return left, right


def _fit_spectrum_candidate(
    frequency,
    sed,
    peak_indices,
    start,
    end,
    baseline_model,
    initial_hwhm,
    peak_max_hwhm,
    fitting_function="lorentz",
):
    """Fit one detected peak cluster with fixed line and baseline models."""

    if baseline_model not in _BASELINE_MODELS:
        raise ValueError(f"unsupported baseline model '{baseline_model}'")
    if fitting_function not in _FITTING_FUNCTIONS:
        raise ValueError(
            f"unsupported fitting function '{fitting_function}'"
        )

    peak_indices = np.asarray(peak_indices, dtype=int)
    order = np.argsort(frequency[peak_indices])
    peak_indices = peak_indices[order]
    initial_hwhm = np.broadcast_to(
        np.asarray(initial_hwhm, dtype=float),
        peak_indices.shape,
    )[order]

    xarr = np.asarray(frequency[start : end + 1], dtype=float)
    values = np.asarray(sed[start : end + 1], dtype=float)
    num_peaks = peak_indices.size
    baseline_count = _baseline_parameter_count(baseline_model)
    num_parameters = 3 * num_peaks + baseline_count
    if xarr.size <= num_parameters + 1:
        raise ValueError(
            "the joint fitting interval has too few frequency samples"
        )

    edges = (float(xarr[0]), float(xarr[-1]))
    edge_baseline = _initial_edge_baseline(values)
    if baseline_model == "none":
        baseline_at_peaks = np.zeros(num_peaks)
    elif baseline_model == "constant":
        baseline_at_peaks = np.full(
            num_peaks,
            np.mean(edge_baseline),
        )
    else:
        baseline_at_peaks = np.interp(
            frequency[peak_indices],
            edges,
            edge_baseline,
        )

    spacing = np.diff(xarr)
    positive_spacing = spacing[spacing > 0]
    if not positive_spacing.size:
        raise ValueError("the fitting frequency axis must be increasing")
    frequency_step = float(np.median(positive_spacing))
    if (
        fitting_function == "dho"
        and np.any(frequency[peak_indices] <= frequency_step)
    ):
        raise ValueError(
            "velocity DHO is not identifiable for a zero-frequency peak"
        )
    minimum_hwhm = max(
        frequency_step * 1.0e-6,
        np.finfo(float).eps,
    )
    user_maximum_hwhm = max(
        float(peak_max_hwhm),
        10.0 * minimum_hwhm,
    )
    centers = frequency[peak_indices]
    center_edges = np.empty(num_peaks + 1, dtype=float)
    center_edges[0] = edges[0]
    center_edges[-1] = edges[-1]
    if num_peaks > 1:
        center_edges[1:-1] = 0.5 * (centers[:-1] + centers[1:])
    peak_cell_widths = np.diff(center_edges)
    adaptive_maximum_hwhm = np.minimum(
        user_maximum_hwhm,
        np.maximum.reduce(
            (
                _ADAPTIVE_HWHM_FACTOR * initial_hwhm,
                np.full(num_peaks, _ADAPTIVE_HWHM_MIN_BINS * frequency_step),
                0.25 * peak_cell_widths,
            )
        ),
    )

    peak_scale = max(float(np.max(values)), np.finfo(float).tiny)
    p0 = []
    lower = []
    upper = []
    for peak_number, (peak_index, hwhm_guess, maximum_hwhm) in enumerate(
        zip(peak_indices, initial_hwhm, adaptive_maximum_hwhm)
    ):
        amplitude_guess = max(
            float(sed[peak_index]) - baseline_at_peaks[peak_number],
            peak_scale * 1.0e-6,
        )
        hwhm_guess = float(
            np.clip(
                hwhm_guess,
                10.0 * minimum_hwhm,
                0.95 * maximum_hwhm,
            )
        )
        center_lower = center_edges[peak_number]
        center_upper = center_edges[peak_number + 1]
        if fitting_function == "dho":
            center_lower = max(0.0, center_lower)
        center_guess = float(
            np.clip(
                centers[peak_number],
                center_lower + minimum_hwhm,
                center_upper - minimum_hwhm,
            )
        )

        p0.extend([center_guess, amplitude_guess, hwhm_guess])
        lower.extend([center_lower, 0.0, minimum_hwhm])
        upper.extend(
            [
                center_upper,
                max(10.0 * peak_scale, 5.0 * amplitude_guess),
                maximum_hwhm,
            ]
        )

    baseline_upper = max(2.0 * peak_scale, np.finfo(float).tiny)
    if baseline_model == "constant":
        p0.append(float(np.mean(edge_baseline)))
        lower.append(0.0)
        upper.append(baseline_upper)
    elif baseline_model == "linear":
        p0.extend(edge_baseline)
        lower.extend([0.0, 0.0])
        upper.extend([baseline_upper, baseline_upper])

    model = _make_multi_peak_model(
        num_peaks,
        baseline_model,
        edges,
        fitting_function=fitting_function,
    )
    optimal, covariance = curve_fit(
        model,
        xarr,
        values,
        p0=np.asarray(p0),
        bounds=(np.asarray(lower), np.asarray(upper)),
        maxfev=100000,
    )
    predicted = model(xarr, *optimal)
    residuals = values - predicted
    errors = np.sqrt(np.maximum(np.diag(covariance), 0.0))

    peak_parameters = optimal[: 3 * num_peaks].reshape(num_peaks, 3)
    peak_errors = errors[: 3 * num_peaks].reshape(num_peaks, 3)
    raw_baseline = optimal[3 * num_peaks :]
    baseline_curve = _baseline_from_raw_parameters(
        xarr,
        baseline_model,
        raw_baseline,
        edges,
    )
    peak_function = _line_shape_function(fitting_function)
    component_curves = np.array(
        [peak_function(xarr, *parameters) for parameters in peak_parameters]
    )
    upper_bound_hits = (
        peak_parameters[:, 2] >= 0.98 * adaptive_maximum_hwhm
    )
    unresolved_widths = peak_parameters[:, 2] < 0.5 * frequency_step

    return {
        "baseline_model": baseline_model,
        "fitting_function": fitting_function,
        "baseline_parameters": _reported_baseline_parameters(
            baseline_model,
            raw_baseline,
            edges,
        ),
        "frequency": xarr,
        "observed": values,
        "predicted": predicted,
        "baseline_curve": baseline_curve,
        "component_curves": component_curves,
        "peak_parameters": peak_parameters,
        "peak_errors": peak_errors,
        "maximum_hwhm": adaptive_maximum_hwhm,
        "upper_bound_hits": upper_bound_hits,
        "unresolved_widths": unresolved_widths,
        "aicc": _aicc(residuals, num_parameters),
        "rss": float(np.dot(residuals, residuals)),
        "fit_start": edges[0],
        "fit_end": edges[1],
        "num_points": xarr.size,
    }


def _fit_lorentzian_candidate(
    frequency,
    sed,
    peak_indices,
    start,
    end,
    baseline_model,
    initial_hwhm,
    peak_max_hwhm,
):
    """Backward-compatible Lorentz-only candidate fitter."""

    return _fit_spectrum_candidate(
        frequency,
        sed,
        peak_indices,
        start,
        end,
        baseline_model,
        initial_hwhm,
        peak_max_hwhm,
        fitting_function="lorentz",
    )


def _fit_spectrum_cluster(
    frequency,
    sed,
    peak_indices,
    start,
    end,
    baseline_model="auto",
    initial_hwhm=0.001,
    peak_max_hwhm=1.0e6,
    fitting_function="lorentz",
):
    """Fit a cluster and select requested line/baseline models with AICc."""

    requested_baselines = (
        _BASELINE_MODELS
        if baseline_model == "auto"
        else (baseline_model,)
    )
    requested_functions = (
        _FITTING_FUNCTIONS
        if fitting_function == "auto"
        else (fitting_function,)
    )
    candidates = []
    errors = []
    for candidate_function in requested_functions:
        for candidate_baseline in requested_baselines:
            try:
                candidates.append(
                    _fit_spectrum_candidate(
                        frequency,
                        sed,
                        peak_indices,
                        start,
                        end,
                        candidate_baseline,
                        initial_hwhm,
                        peak_max_hwhm,
                        fitting_function=candidate_function,
                    )
                )
            except (RuntimeError, TypeError, ValueError) as error:
                errors.append(
                    f"{candidate_function}/{candidate_baseline}: {error}"
                )

    if not candidates:
        raise RuntimeError("; ".join(errors) or "all spectrum fits failed")
    if baseline_model != "auto" and fitting_function != "auto":
        return candidates[0]

    # A candidate that turns a peak into an adaptive-width boundary is not a
    # trustworthy background/peak decomposition. Prefer non-degenerate fits
    # whenever at least one is available, then apply ordinary AICc selection.
    regular_candidates = [
        candidate
        for candidate in candidates
        if not np.any(candidate["upper_bound_hits"])
    ]
    if regular_candidates:
        candidates = regular_candidates

    if fitting_function == "auto":
        distinguishable_candidates = []
        for candidate in candidates:
            if candidate["fitting_function"] != "dho":
                distinguishable_candidates.append(candidate)
                continue
            parameters = candidate["peak_parameters"]
            positive_centers = parameters[:, 0] > 0.0
            damping_ratios = np.zeros(len(parameters), dtype=float)
            damping_ratios[positive_centers] = (
                parameters[positive_centers, 2]
                / parameters[positive_centers, 0]
            )
            if np.any(
                damping_ratios
                >= _DHO_MIN_DISTINGUISHABLE_DAMPING_RATIO
            ):
                distinguishable_candidates.append(candidate)
        if any(
            candidate["fitting_function"] == "lorentz"
            for candidate in distinguishable_candidates
        ):
            candidates = distinguishable_candidates

    best_aicc = min(candidate["aicc"] for candidate in candidates)
    statistically_equivalent = [
        candidate
        for candidate in candidates
        if candidate["aicc"] <= best_aicc + _AUTO_AICC_EQUIVALENCE
    ]
    return min(
        statistically_equivalent,
        key=lambda candidate: (
            _baseline_parameter_count(candidate["baseline_model"]),
            0 if candidate["fitting_function"] == "lorentz" else 1,
        ),
    )


def _fit_lorentzian_cluster(
    frequency,
    sed,
    peak_indices,
    start,
    end,
    baseline_model="auto",
    initial_hwhm=0.001,
    peak_max_hwhm=1.0e6,
):
    """Backward-compatible Lorentz-only cluster fitter."""

    return _fit_spectrum_cluster(
        frequency,
        sed,
        peak_indices,
        start,
        end,
        baseline_model=baseline_model,
        initial_hwhm=initial_hwhm,
        peak_max_hwhm=peak_max_hwhm,
        fitting_function="lorentz",
    )


def _safe_peak_interval(start, end, peak, size, modulate_factor):
    """Return a bounded fit interval that retains the detected peak."""

    start = int(start) + modulate_factor
    end = int(end) - modulate_factor
    if start >= peak:
        start = max(0, int(peak) - 2)
    if end <= peak:
        end = min(size - 1, int(peak) + 2)
    return max(0, start), min(size - 1, end)


def _local_peak_intervals(
    peaks,
    properties,
    modulate_factor,
    size,
    sed=None,
):
    """Build non-overlapping peak windows bounded by neighboring valleys."""

    peaks = np.asarray(peaks, dtype=int)
    if not peaks.size:
        return []

    valleys = []
    if sed is not None:
        sed = np.asarray(sed, dtype=float)
        for left_peak, right_peak in zip(peaks[:-1], peaks[1:]):
            section = sed[left_peak : right_peak + 1]
            valleys.append(left_peak + int(np.argmin(section)))
    else:
        valleys = [
            int((left_peak + right_peak) // 2)
            for left_peak, right_peak in zip(peaks[:-1], peaks[1:])
        ]

    intervals = []
    for peak_number, peak in enumerate(peaks):
        start = (
            0
            if peak_number == 0
            else valleys[peak_number - 1]
        )
        end = (
            size - 1
            if peak_number == peaks.size - 1
            else valleys[peak_number]
        )
        start, end = _safe_peak_interval(
            start,
            end,
            peak,
            size,
            modulate_factor,
        )
        intervals.append(
            {
                "start": start,
                "end": end,
                "peak_numbers": [peak_number],
                "strategy": "independent",
            }
        )
    return intervals


def _merge_intervals(intervals, should_merge, strategy):
    """Merge adjacent intervals according to a caller-provided predicate."""

    clusters = []
    for interval in intervals:
        if clusters and should_merge(clusters[-1], interval):
            clusters[-1]["start"] = min(
                clusters[-1]["start"],
                interval["start"],
            )
            clusters[-1]["end"] = max(
                clusters[-1]["end"],
                interval["end"],
            )
            clusters[-1]["peak_numbers"].extend(
                interval["peak_numbers"]
            )
            clusters[-1]["strategy"] = strategy
        else:
            clusters.append(dict(interval))
            clusters[-1]["strategy"] = strategy
    return clusters


def _build_peak_clusters(
    peaks,
    properties,
    modulate_factor,
    size,
    strategy="joint",
    sed=None,
    width_intervals=None,
):
    """Build independent, forced-joint, or overlap-aware peak clusters."""

    local_intervals = _local_peak_intervals(
        peaks,
        properties,
        modulate_factor,
        size,
        sed=sed,
    )
    if strategy == "independent" or not local_intervals:
        return local_intervals

    if strategy in {"auto", "joint"} and width_intervals is not None:
        left_ips, right_ips = (
            np.asarray(width_intervals[0], dtype=float),
            np.asarray(width_intervals[1], dtype=float),
        )
        widths = right_ips - left_ips
        expansion = (
            _AUTO_OVERLAP_EXPANSION
            if strategy == "auto"
            else _JOINT_OVERLAP_EXPANSION
        )
        pad = 0.5 * (expansion - 1.0) * widths
        overlap_left = left_ips - pad
        overlap_right = right_ips + pad

        clusters = []
        for peak_number, interval in enumerate(local_intervals):
            if (
                clusters
                and overlap_left[peak_number]
                <= clusters[-1]["overlap_right"]
            ):
                clusters[-1]["end"] = interval["end"]
                clusters[-1]["peak_numbers"].append(peak_number)
                clusters[-1]["overlap_right"] = max(
                    clusters[-1]["overlap_right"],
                    overlap_right[peak_number],
                )
                clusters[-1]["strategy"] = "joint"
            else:
                candidate = dict(interval)
                candidate["overlap_right"] = overlap_right[peak_number]
                clusters.append(candidate)
        for cluster in clusters:
            cluster.pop("overlap_right", None)
        return clusters

    # Fallback for callers that do not provide half-height intervals.
    prominence_intervals = []
    for peak_number, peak in enumerate(peaks):
        start, end = _safe_peak_interval(
            properties["left_bases"][peak_number],
            properties["right_bases"][peak_number],
            peak,
            size,
            modulate_factor,
        )
        prominence_intervals.append(
            {
                "start": start,
                "end": end,
                "peak_numbers": [peak_number],
            }
        )
    prominence_intervals.sort(
        key=lambda interval: (interval["start"], interval["end"])
    )
    return _merge_intervals(
        prominence_intervals,
        lambda left, right: right["start"] <= left["end"],
        "joint",
    )


def _expand_cluster_interval(cluster, peaks, size, baseline_model):
    """Ensure a cluster contains enough samples for every candidate model."""

    num_peaks = len(cluster["peak_numbers"])
    baseline_count = 2 if baseline_model in {"linear", "auto"} else (
        1 if baseline_model == "constant" else 0
    )
    required = 3 * num_peaks + baseline_count + 2
    start = cluster["start"]
    end = cluster["end"]
    while end - start + 1 < required and (start > 0 or end < size - 1):
        if start > 0:
            start -= 1
        if end - start + 1 >= required:
            break
        if end < size - 1:
            end += 1

    cluster = dict(cluster)
    cluster["start"] = start
    cluster["end"] = end
    cluster["peaks"] = np.asarray(
        [peaks[number] for number in cluster["peak_numbers"]],
        dtype=int,
    )
    return cluster


class lorentz:
    """Detect SED peaks and fit configurable line-shape clusters."""

    def __init__(self, data, params):
        self.q_index = params.qpoint_slice_index
        self.lorentz_fit_freq_min = getattr(
            params,
            "lorentz_fit_freq_min",
            None,
        )
        self.lorentz_fit_freq_max = getattr(
            params,
            "lorentz_fit_freq_max",
            None,
        )
        self.fit_baseline_model = getattr(
            params,
            "fit_baseline_model",
            "auto",
        )
        self.fit_peak_strategy = getattr(
            params,
            "fit_peak_strategy",
            "auto",
        )
        self.fitting_function = getattr(
            params,
            "fitting_function",
            "lorentz",
        )

        selected_frequency, selected_sed = _select_lorentz_frequency_range(
            data.freq_fft,
            data.sed_avg[:, self.q_index],
            freq_min=self.lorentz_fit_freq_min,
            freq_max=self.lorentz_fit_freq_max,
        )
        if (
            self.lorentz_fit_freq_min is not None
            or self.lorentz_fit_freq_max is not None
        ):
            print(
                "      Frequency range      : "
                f"{selected_frequency.min():.3f}-"
                f"{selected_frequency.max():.3f} THz\n"
            )

        # Mirror only a spectrum that actually starts at zero. This makes a
        # possible acoustic/DC endpoint maximum detectable by find_peaks.
        mirror_points = min(5, selected_sed.size - 1)
        starts_at_zero = np.isclose(selected_frequency[0], 0.0)
        if mirror_points and starts_at_zero:
            self.sed = np.concatenate(
                [selected_sed[1 : mirror_points + 1][::-1], selected_sed]
            )
            self.thz = np.concatenate(
                [
                    -selected_frequency[1 : mirror_points + 1][::-1],
                    selected_frequency,
                ]
            )
        else:
            self.sed = np.asarray(selected_sed, dtype=float)
            self.thz = np.asarray(selected_frequency, dtype=float)

        peaks, properties, peak_significance = _find_sed_peaks(
            self.sed,
            peak_min_significance=getattr(
                params,
                "peak_min_significance",
                None,
            ),
            peak_height=params.peak_height,
            peak_prominence=params.peak_prominence,
        )

        # The mirrored half is only detection support. Keep each physical,
        # non-negative-frequency peak exactly once.
        keep = self.thz[peaks] >= 0.0
        peaks = peaks[keep]
        properties = {
            name: values[keep]
            for name, values in properties.items()
        }
        if peak_significance is not None:
            peak_significance = peak_significance[keep]
        else:
            peak_significance = np.full(len(peaks), np.nan, dtype=float)

        width_results = peak_widths(self.sed, peaks, rel_height=0.5)
        widths = width_results[0]
        frequency_step = float(np.median(np.diff(self.thz)))
        width_hwhm = 0.5 * widths * frequency_step
        initial_hwhm = np.maximum(
            width_hwhm,
            float(params.initial_guess_hwhm),
        )

        print("  >  Peak detection")
        print(f"      Peaks found          : {len(peaks)}")
        if params.peak_min_significance is not None:
            print(
                "      Minimum significance : "
                f"{params.peak_min_significance:g}"
            )
        print(f"      Baseline requested   : {self.fit_baseline_model}")
        print(f"      Peak strategy        : {self.fit_peak_strategy}")
        print(f"      Fitting function     : {self.fitting_function}")
        fit_figure = Plot_SED.resolve_slice_output_path(
            params,
            lorentz=True,
        )
        print(f"      Fit figure           : {fit_figure}")
        print()

        clusters = _build_peak_clusters(
            peaks,
            properties,
            params.modulate_factor,
            self.sed.size,
            strategy=self.fit_peak_strategy,
            sed=self.sed,
            width_intervals=(width_results[2], width_results[3]),
        )
        clusters = [
            _expand_cluster_interval(
                cluster,
                peaks,
                self.sed.size,
                self.fit_baseline_model,
            )
            for cluster in clusters
        ]

        self.fit_clusters = []
        for cluster_number, cluster in enumerate(clusters, start=1):
            peak_numbers = cluster["peak_numbers"]
            cluster_hwhm = initial_hwhm[peak_numbers]
            try:
                result = _fit_spectrum_cluster(
                    self.thz,
                    self.sed,
                    cluster["peaks"],
                    cluster["start"],
                    cluster["end"],
                    baseline_model=self.fit_baseline_model,
                    initial_hwhm=cluster_hwhm,
                    peak_max_hwhm=params.peak_max_hwhm,
                    fitting_function=self.fitting_function,
                )
            except RuntimeError as error:
                peak_list = ", ".join(
                    f"{self.thz[peak]:.6f}" for peak in cluster["peaks"]
                )
                print(
                    "  WARNING: spectrum fit failed for peaks at "
                    f"{peak_list} THz: {error}"
                )
                continue

            result["peak_strategy"] = cluster["strategy"]
            result["peak_significance"] = peak_significance[peak_numbers]
            self.fit_clusters.append(result)
            print(
                f"      Cluster {cluster_number:<3d}         : "
                f"{len(cluster['peaks'])} peak(s), "
                f"{result['fit_start']:.4f}-{result['fit_end']:.4f} THz, "
                f"{result['num_points']} points, {cluster['strategy']}"
            )
            print(
                "      Selected baseline    : "
                f"{result['baseline_model']} "
                f"(AICc {result['aicc']:.3f})"
            )
            print(
                "      Selected function    : "
                f"{result['fitting_function']}"
            )
            if np.any(result["upper_bound_hits"]):
                print(
                    "  WARNING: one or more fitted widths reached their "
                    "adaptive upper bound"
                )
            if np.any(result["unresolved_widths"]):
                print(
                    "  WARNING: one or more fitted widths are below half "
                    "a frequency bin"
                )

        if self.fit_clusters:
            flat_parameters = []
            flat_errors = []
            flat_models = []
            flat_strategies = []
            flat_upper_bound_hits = []
            flat_unresolved_widths = []
            flat_peak_significance = []
            for result in self.fit_clusters:
                num_result_peaks = len(result["peak_parameters"])
                flat_parameters.extend(result["peak_parameters"])
                flat_errors.extend(result["peak_errors"])
                flat_models.extend(
                    [result["fitting_function"]] * num_result_peaks
                )
                flat_strategies.extend(
                    [result["peak_strategy"]] * num_result_peaks
                )
                flat_upper_bound_hits.extend(result["upper_bound_hits"])
                flat_unresolved_widths.extend(result["unresolved_widths"])
                flat_peak_significance.extend(result["peak_significance"])
            self.popt = np.asarray(flat_parameters, dtype=float)
            self.pcov = np.asarray(flat_errors, dtype=float)
            self.fit_models = np.asarray(flat_models, dtype=object)
            self.fit_strategies = np.asarray(flat_strategies, dtype=object)
            self.upper_bound_hits = np.asarray(
                flat_upper_bound_hits,
                dtype=bool,
            )
            self.unresolved_widths = np.asarray(
                flat_unresolved_widths,
                dtype=bool,
            )
            self.peak_significance = np.asarray(
                flat_peak_significance,
                dtype=float,
            )
            order = np.argsort(self.popt[:, 0])
            self.popt = self.popt[order]
            self.pcov = self.pcov[order]
            self.fit_models = self.fit_models[order]
            self.fit_strategies = self.fit_strategies[order]
            self.upper_bound_hits = self.upper_bound_hits[order]
            self.unresolved_widths = self.unresolved_widths[order]
            self.peak_significance = self.peak_significance[order]
        else:
            self.popt = np.empty((0, 3), dtype=float)
            self.pcov = np.empty((0, 3), dtype=float)
            self.fit_models = np.empty(0, dtype=object)
            self.fit_strategies = np.empty(0, dtype=object)
            self.upper_bound_hits = np.empty(0, dtype=bool)
            self.unresolved_widths = np.empty(0, dtype=bool)
            self.peak_significance = np.empty(0, dtype=float)

        params.popt = self.popt
        params.pcov = self.pcov
        params.fit_models = self.fit_models
        params.fit_strategies = self.fit_strategies
        params.fit_peak_significance = self.peak_significance
        params.lorentz_fit_clusters = self.fit_clusters
        params.plot_lorentz = True

        FileIO.write_lorentz(self, params)
        lifetime_file = FileIO.write_phonon_lifetime(self, params)

        lifetimes = FileIO.hwhm_to_lifetime_ps(self.popt[:, 2])
        print("\n  >  Spectral peak fit results")
        print("      Lifetime definition  : tau = 1 / (2*pi*HWHM)")
        print(
            "      Frequency (THz)      HWHM (THz)      Lifetime (ps)"
            "      Model"
        )
        print(
            "      ---------------      ----------      -------------"
            "      -------"
        )
        for frequency, hwhm, lifetime, model in zip(
            self.popt[:, 0],
            self.popt[:, 2],
            lifetimes,
            self.fit_models,
        ):
            if np.isfinite(lifetime):
                print(
                    f"      {frequency:15.6f}      {hwhm:10.6f}      "
                    f"{lifetime:13.8f}      {model}"
                )
        print(f"\n  [OK] Lifetime data written: {lifetime_file}")

        Plot_SED.plot_slice(data, params)
