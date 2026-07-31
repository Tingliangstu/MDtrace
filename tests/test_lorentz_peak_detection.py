"""Tests for adaptive SED peak detection."""

import unittest
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import numpy as np

from mdtrace.parser import read_input
from mdtrace.sed.FileIO import (
    hwhm_to_lifetime_ps,
    write_lorentz,
    write_phonon_lifetime,
)
from mdtrace.sed.Lorentz import (
    _build_peak_clusters,
    _fit_lorentzian_cluster,
    _fit_spectrum_cluster,
    _find_sed_peaks,
    _lorentzian,
    _select_lorentz_frequency_range,
    _velocity_dho,
)


def _synthetic_sed():
    frequency = np.linspace(0.0, 20.0, 2001)
    baseline = 2.0e-4 * np.exp(-frequency / 15.0)
    peak_1 = 2.0e-2 / (1.0 + ((frequency - 4.0) / 0.12) ** 2)
    peak_2 = 1.5e-3 / (1.0 + ((frequency - 13.0) / 0.20) ** 2)
    ripple = 1.0 + 0.01 * np.sin(2.0 * np.pi * frequency / 0.37)
    return frequency, (baseline + peak_1 + peak_2) * ripple


class AdaptivePeakDetectionTests(unittest.TestCase):
    def test_hwhm_conversion_matches_reported_lifetime_convention(self):
        hwhm = np.array([0.01, 0.02, 0.0])

        lifetime = hwhm_to_lifetime_ps(hwhm)

        np.testing.assert_allclose(
            lifetime[:2],
            1.0 / (2.0 * np.pi * hwhm[:2]),
        )
        self.assertTrue(np.isnan(lifetime[2]))

    def test_significance_detection_is_invariant_to_linear_scaling(self):
        _, sed = _synthetic_sed()

        peaks, _, significance = _find_sed_peaks(
            sed,
            peak_min_significance=4.0,
        )
        scaled_peaks, _, scaled_significance = _find_sed_peaks(
            1000.0 * sed,
            peak_min_significance=4.0,
        )

        np.testing.assert_array_equal(peaks, scaled_peaks)
        np.testing.assert_allclose(
            significance,
            scaled_significance,
            rtol=1.0e-10,
            atol=1.0e-10,
        )

    def test_absolute_height_remains_an_optional_second_filter(self):
        frequency, sed = _synthetic_sed()

        peaks, _, _ = _find_sed_peaks(
            sed,
            peak_min_significance=4.0,
        )
        filtered_peaks, _, _ = _find_sed_peaks(
            sed,
            peak_min_significance=4.0,
            peak_height=5.0e-3,
        )

        self.assertTrue(np.any(np.isclose(frequency[peaks], 13.0, atol=0.1)))
        self.assertFalse(
            np.any(np.isclose(frequency[filtered_peaks], 13.0, atol=0.1))
        )
        self.assertTrue(
            np.any(np.isclose(frequency[filtered_peaks], 4.0, atol=0.1))
        )

    def test_parser_reads_and_validates_peak_min_significance(self):
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "action = fit\npeak_min_significance = 4.0\n",
                encoding="utf-8",
            )

            params = read_input(input_file)

            self.assertEqual(params.peak_min_significance, 4.0)

            input_file.write_text(
                "action = fit\npeak_min_significance = 0\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "peak_min_significance must be positive and finite",
            ):
                read_input(input_file)

    def test_lorentz_frequency_range_is_inclusive(self):
        frequency = np.arange(0.0, 8.0)
        sed = 10.0 + frequency

        selected_frequency, selected_sed = (
            _select_lorentz_frequency_range(
                frequency,
                sed,
                freq_min=2.0,
                freq_max=5.0,
            )
        )

        np.testing.assert_array_equal(
            selected_frequency,
            np.array([2.0, 3.0, 4.0, 5.0]),
        )
        np.testing.assert_array_equal(
            selected_sed,
            np.array([12.0, 13.0, 14.0, 15.0]),
        )

    def test_parser_reads_and_validates_lorentz_frequency_range(self):
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "action = fit\n"
                "lorentz_fit_freq_min = 2.0\n"
                "lorentz_fit_freq_max = 5.0\n",
                encoding="utf-8",
            )

            params = read_input(input_file)

            self.assertEqual(params.lorentz_fit_freq_min, 2.0)
            self.assertEqual(params.lorentz_fit_freq_max, 5.0)

            invalid_cases = (
                (
                    "lorentz_fit_freq_min = -1\n",
                    "lorentz_fit_freq_min must be non-negative and finite",
                ),
                (
                    "lorentz_fit_freq_max = 0\n",
                    "lorentz_fit_freq_max must be positive and finite",
                ),
                (
                    "lorentz_fit_freq_min = 5\n"
                    "lorentz_fit_freq_max = 5\n",
                    "lorentz_fit_freq_min must be smaller",
                ),
            )
            for settings, message in invalid_cases:
                with self.subTest(settings=settings):
                    input_file.write_text(
                        f"action = fit\n{settings}",
                        encoding="utf-8",
                    )
                    with self.assertRaisesRegex(ValueError, message):
                        read_input(input_file)

    def test_parser_reads_and_validates_fit_baseline_model(self):
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            for model in ("none", "constant", "linear", "auto"):
                with self.subTest(model=model):
                    input_file.write_text(
                        f"action = fit\nfit_baseline_model = {model}\n",
                        encoding="utf-8",
                    )
                    params = read_input(input_file)
                    self.assertEqual(params.fit_baseline_model, model)

            input_file.write_text(
                "action = fit\nfit_baseline_model = quadratic\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                ValueError,
                "fit_baseline_model must be one of",
            ):
                read_input(input_file)

    def test_parser_reads_and_validates_peak_strategy_and_function(self):
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            for strategy in ("independent", "joint", "auto"):
                with self.subTest(strategy=strategy):
                    input_file.write_text(
                        "action = fit\n"
                        f"fit_peak_strategy = {strategy}\n",
                        encoding="utf-8",
                    )
                    params = read_input(input_file)
                    self.assertEqual(params.fit_peak_strategy, strategy)

            for function in ("lorentz", "dho", "auto"):
                with self.subTest(function=function):
                    input_file.write_text(
                        "action = fit\n"
                        f"fitting_function = {function}\n",
                        encoding="utf-8",
                    )
                    params = read_input(input_file)
                    self.assertEqual(params.fitting_function, function)

            for setting, message in (
                (
                    "fit_peak_strategy = global\n",
                    "fit_peak_strategy must be one of",
                ),
                (
                    "fitting_function = gaussian\n",
                    "fitting_function must be one of",
                ),
            ):
                input_file.write_text(
                    f"action = fit\n{setting}",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(ValueError, message):
                    read_input(input_file)

    def test_velocity_dho_uses_peak_height_and_equivalent_hwhm(self):
        center = 2.0
        amplitude = 3.0
        hwhm = 0.25
        damping_width = 2.0 * hwhm
        root = np.sqrt(4.0 * center**2 + damping_width**2)
        half_max_frequencies = np.array(
            [
                0.5 * (root - damping_width),
                0.5 * (root + damping_width),
            ]
        )

        self.assertAlmostEqual(
            _velocity_dho(center, center, amplitude, hwhm),
            amplitude,
        )
        np.testing.assert_allclose(
            _velocity_dho(
                half_max_frequencies,
                center,
                amplitude,
                hwhm,
            ),
            0.5 * amplitude,
        )
        self.assertAlmostEqual(
            np.diff(half_max_frequencies)[0],
            2.0 * hwhm,
        )

    def test_overdamped_dho_is_diagnosed_and_omitted_from_lifetime(self):
        fit = SimpleNamespace(
            popt=np.array([[1.0, 2.0, 0.2], [0.1, 1.0, 0.2]]),
            pcov=np.zeros((2, 3)),
            fit_clusters=[],
            fit_models=np.array(["dho", "dho"], dtype=object),
            fit_strategies=np.array(
                ["independent", "independent"],
                dtype=object,
            ),
            upper_bound_hits=np.zeros(2, dtype=bool),
            unresolved_widths=np.zeros(2, dtype=bool),
        )
        params = SimpleNamespace(out_files_name="test", qpoint_slice_index=0)

        with TemporaryDirectory() as directory:
            original = os.getcwd()
            try:
                os.chdir(directory)
                write_lorentz(fit, params)
                lifetime_file = write_phonon_lifetime(fit, params)
                model_text = Path("test_LORENTZ-0.models").read_text(
                    encoding="utf-8"
                )
                lifetime_lines = Path(lifetime_file).read_text(
                    encoding="utf-8"
                ).splitlines()
            finally:
                os.chdir(original)

        self.assertIn("underdamped", model_text)
        self.assertIn("overdamped", model_text)
        self.assertEqual(len(lifetime_lines), 3)
        self.assertTrue(lifetime_lines[2].startswith("1.000000 "))

    def test_auto_function_selects_dho_for_broad_velocity_spectrum(self):
        frequency = np.linspace(0.05, 4.0, 500)
        expected = np.array([1.0, 2.0, 0.4])
        sed = 0.02 + _velocity_dho(frequency, *expected)
        peak = np.array([np.argmin(np.abs(frequency - expected[0]))])

        result = _fit_spectrum_cluster(
            frequency,
            sed,
            peak,
            0,
            len(frequency) - 1,
            baseline_model="auto",
            initial_hwhm=expected[2],
            peak_max_hwhm=2.0,
            fitting_function="auto",
        )

        self.assertEqual(result["fitting_function"], "dho")
        self.assertEqual(result["baseline_model"], "constant")
        np.testing.assert_allclose(
            result["peak_parameters"][0],
            expected,
            rtol=1.0e-6,
            atol=1.0e-8,
        )

    def test_auto_function_prefers_lorentz_in_weak_damping_limit(self):
        frequency = np.linspace(1.0, 3.0, 500)
        expected = np.array([2.0, 1.0, 0.02])
        sed = 0.01 + _velocity_dho(frequency, *expected)
        peak = np.array([np.argmin(np.abs(frequency - expected[0]))])

        result = _fit_spectrum_cluster(
            frequency,
            sed,
            peak,
            0,
            len(frequency) - 1,
            baseline_model="auto",
            initial_hwhm=expected[2],
            peak_max_hwhm=1.0,
            fitting_function="auto",
        )

        self.assertEqual(result["fitting_function"], "lorentz")

    def test_auto_strategy_only_joins_overlapping_width_support(self):
        peaks = np.array([20, 26, 80])
        properties = {
            "left_bases": np.array([10, 21, 70]),
            "right_bases": np.array([25, 40, 90]),
        }
        sed = np.ones(101)
        sed[23] = 0.0
        sed[50] = 0.0
        width_intervals = (
            np.array([17.0, 23.0, 78.0]),
            np.array([23.0, 29.0, 82.0]),
        )

        independent = _build_peak_clusters(
            peaks,
            properties,
            0,
            len(sed),
            strategy="independent",
            sed=sed,
            width_intervals=width_intervals,
        )
        automatic = _build_peak_clusters(
            peaks,
            properties,
            0,
            len(sed),
            strategy="auto",
            sed=sed,
            width_intervals=width_intervals,
        )

        self.assertEqual([len(c["peak_numbers"]) for c in independent], [1, 1, 1])
        self.assertEqual([len(c["peak_numbers"]) for c in automatic], [2, 1])
        self.assertEqual(automatic[0]["strategy"], "joint")

    def test_joint_strategy_uses_broader_overlap_than_auto(self):
        peaks = np.array([20, 38, 80])
        properties = {
            "left_bases": np.array([10, 25, 70]),
            "right_bases": np.array([30, 50, 90]),
        }
        sed = np.ones(101)
        sed[29] = 0.0
        sed[55] = 0.0
        width_intervals = (
            np.array([17.0, 35.0, 78.0]),
            np.array([23.0, 41.0, 82.0]),
        )

        automatic = _build_peak_clusters(
            peaks,
            properties,
            0,
            len(sed),
            strategy="auto",
            sed=sed,
            width_intervals=width_intervals,
        )
        joint = _build_peak_clusters(
            peaks,
            properties,
            0,
            len(sed),
            strategy="joint",
            sed=sed,
            width_intervals=width_intervals,
        )

        self.assertEqual([len(c["peak_numbers"]) for c in automatic], [1, 1, 1])
        self.assertEqual([len(c["peak_numbers"]) for c in joint], [2, 1])

    def test_joint_linear_baseline_recovers_overlapping_peaks(self):
        frequency = np.linspace(4.0, 6.0, 401)
        expected = np.array(
            [
                [4.80, 1.00, 0.08],
                [5.25, 0.65, 0.12],
            ]
        )
        sed = 0.12 + 0.04 * (frequency - 5.0)
        for parameters in expected:
            sed += _lorentzian(frequency, *parameters)
        peaks = np.array(
            [np.argmin(np.abs(frequency - center)) for center in expected[:, 0]]
        )

        result = _fit_lorentzian_cluster(
            frequency,
            sed,
            peaks,
            0,
            len(frequency) - 1,
            baseline_model="linear",
            initial_hwhm=expected[:, 2],
            peak_max_hwhm=1.0,
        )

        np.testing.assert_allclose(
            result["peak_parameters"],
            expected,
            rtol=1.0e-6,
            atol=1.0e-8,
        )
        np.testing.assert_allclose(
            result["baseline_parameters"],
            np.array([0.12, 0.04]),
            rtol=1.0e-6,
            atol=1.0e-8,
        )

    def test_auto_baseline_selects_linear_for_sloped_background(self):
        frequency = np.linspace(4.0, 6.0, 401)
        expected = np.array(
            [
                [4.80, 1.00, 0.08],
                [5.25, 0.65, 0.12],
            ]
        )
        sed = 0.12 + 0.04 * (frequency - 5.0)
        for parameters in expected:
            sed += _lorentzian(frequency, *parameters)
        peaks = np.array(
            [np.argmin(np.abs(frequency - center)) for center in expected[:, 0]]
        )

        result = _fit_lorentzian_cluster(
            frequency,
            sed,
            peaks,
            0,
            len(frequency) - 1,
            baseline_model="auto",
            initial_hwhm=expected[:, 2],
            peak_max_hwhm=1.0,
        )

        self.assertEqual(result["baseline_model"], "linear")
        np.testing.assert_allclose(
            hwhm_to_lifetime_ps(result["peak_parameters"][:, 2]),
            hwhm_to_lifetime_ps(expected[:, 2]),
            rtol=1.0e-6,
        )

    def test_default_keeps_adaptive_detection_disabled(self):
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text("action = fit\n", encoding="utf-8")

            params = read_input(input_file)

            self.assertIsNone(params.peak_min_significance)
            self.assertIsNone(params.lorentz_fit_freq_min)
            self.assertIsNone(params.lorentz_fit_freq_max)
            self.assertEqual(params.fit_baseline_model, "auto")
            self.assertEqual(params.fit_peak_strategy, "auto")
            self.assertEqual(params.fitting_function, "lorentz")


if __name__ == "__main__":
    unittest.main()
