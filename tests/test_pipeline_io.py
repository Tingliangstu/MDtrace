"""CLI parser-to-pipeline trajectory integration tests."""

import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mdtrace.parser import read_input
from mdtrace.pipeline import step_prepare_trajectory

NETCDF4_AVAILABLE = importlib.util.find_spec("netCDF4") is not None

GPUMD_TEXT = """\
1
Lattice="5 0 0 0 5 0 0 0 5" Properties=species:S:1:pos:R:3:vel:R:3
Si 0 0 0 0.001 0.002 0.003
"""


class ParserTests(unittest.TestCase):
    def test_single_trajectory_configuration(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            basis_file = root / "basis.in"
            basis_file.write_text(
                "test structure\n"
                "atoms_ids unitcell_index basis_index mass_types\n"
                "1 1 1 15.9994\n",
                encoding="utf-8",
            )
            input_file = root / "input.in"
            input_file.write_text(
                "action = plot\n"
                "trajectory_file = movie.nc\n"
                "lammps_unit = metal\n"
                "netcdf_compression_level = 0\n"
                "netcdf_batch_size = 64\n"
                "output_partial = 1\n"
                f"basis_lattice_file = {basis_file}\n"
                "plot_partial_SED = O y\n",
                encoding="utf-8",
            )

            params = read_input(str(input_file))

            self.assertEqual(
                params.trajectory_file,
                str((root / "movie.nc").resolve()),
            )
            self.assertEqual(params.lammps_unit, "metal")
            self.assertEqual(params.netcdf_compression_level, 0)
            self.assertEqual(params.netcdf_batch_size, 64)
            self.assertFalse(hasattr(params, "trajectory_path"))
            self.assertFalse(hasattr(params, "source_format"))
            self.assertTrue(params.output_partial)
            self.assertEqual(params.plot_partial_element, "O")
            self.assertEqual(params.plot_partial_type, 0)
            self.assertEqual(params.plot_partial_dir, "y")

    def test_netcdf_tuning_parameters_are_validated(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            for setting, message in (
                ("netcdf_compression_level = 10", "between 0 and 9"),
                ("netcdf_batch_size = 0", "must be positive"),
            ):
                input_file.write_text(
                    f"action = plot\n{setting}\n",
                    encoding="utf-8",
                )
                with (
                    self.subTest(setting=setting),
                    self.assertRaisesRegex(ValueError, message),
                ):
                    read_input(str(input_file))

    def test_partial_sed_rejects_unknown_element(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "plot_partial_SED = NotAnElement y\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "was not found in the periodic table",
            ):
                read_input(str(input_file))

    def test_partial_sed_element_must_exist_in_structure(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            basis_file = root / "basis.in"
            basis_file.write_text(
                "test structure\n"
                "atoms_ids unitcell_index basis_index mass_types\n"
                "1 1 1 28.0855\n",
                encoding="utf-8",
            )
            input_file = root / "input.in"
            input_file.write_text(
                "action = plot\n"
                f"basis_lattice_file = {basis_file}\n"
                "plot_partial_SED = O y\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "was not found in the input structure",
            ):
                read_input(str(input_file))

    def test_sed_and_dsf_parameters_are_separate(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            sed_input = root / "sed.in"
            sed_input.write_text(
                "method = sed\n"
                "action = plot\n"
                "num_blocks = 4\n"
                "max_cores = 2\n",
                encoding="utf-8",
            )
            dsf_input = root / "dsf.in"
            dsf_input.write_text(
                "method = dsf\n"
                "action = plot\n"
                "num_blocks = 8\n"
                "max_cores = 3\n",
                encoding="utf-8",
            )

            sed_params = read_input(str(sed_input))
            dsf_params = read_input(str(dsf_input))

            self.assertEqual(sed_params.method, "sed")
            self.assertEqual(sed_params.num_blocks, 4)
            self.assertEqual(sed_params.max_cores, 2)
            self.assertFalse(hasattr(sed_params, "experiment"))

            self.assertEqual(dsf_params.method, "dsf")
            self.assertEqual(dsf_params.num_blocks, 8)
            self.assertEqual(dsf_params.max_cores, 3)
            self.assertFalse(hasattr(dsf_params, "num_qpaths"))

    def test_method_specific_parameter_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "method = sed\n"
                "action = plot\n"
                "experiment = neutron\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "is not valid for method 'sed'",
            ):
                read_input(input_file)

    def test_malformed_inputs_are_rejected(self) -> None:
        cases = {
            "missing_equals": (
                "action plot\n",
                "expected 'key = value'",
            ),
            "unknown_parameter": (
                "action = plot\nnum_atom = 10\n",
                "parameter 'num_atom' is not valid",
            ),
            "extra_scalar_value": (
                "action = plot\nnum_atoms = 10 extra\n",
                "requires exactly 1 value",
            ),
            "duplicate_parameter": (
                "action = plot\naction = fit\n",
                "parameter 'action' is repeated",
            ),
            "invalid_boolean": (
                "action = plot\noutput_partial = 2\n",
                "must be 0 or 1",
            ),
            "invalid_backend": (
                "action = plot\nbackend = unknown\n",
                "backend 'unknown' is not available",
            ),
        }
        with TemporaryDirectory() as directory:
            root = Path(directory)
            for name, (text, message) in cases.items():
                with self.subTest(name=name):
                    input_file = root / f"{name}.in"
                    input_file.write_text(text, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, message):
                        read_input(input_file)

    def test_planned_options_are_accepted(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "method = dsf\n"
                "action = future_action\n"
                "backend = cupy\n"
                "experiment = xray\n",
                encoding="utf-8",
            )

            params = read_input(input_file)

            self.assertEqual(params.action, "future_action")
            self.assertEqual(params.backend, "cupy")
            self.assertEqual(params.experiment, "xray")

    def test_q_path_labels_are_validated(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "action = plot\n"
                "num_qpaths = 2\n"
                "q_path_name = GX\n"
                "q_path = 0 0 0  0.5 0 0  0.5 0.5 0\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "q_path_name requires 3 labels",
            ):
                read_input(input_file)

    def test_compute_requires_positive_sampling_values(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text(
                "action = compute\n"
                "time_step = 0\n"
                "output_data_stride = 1\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ValueError,
                "time_step must be positive",
            ):
                read_input(input_file)

    def test_eels_method_is_recognized(self) -> None:
        with TemporaryDirectory() as directory:
            input_file = Path(directory) / "input.in"
            input_file.write_text("method = eels\n", encoding="utf-8")

            params = read_input(str(input_file))

            self.assertEqual(params.method, "eels")
            self.assertEqual(params.num_blocks, 5)
            self.assertEqual(params.max_cores, 4)

    @unittest.skipUnless(NETCDF4_AVAILABLE, "netCDF4 is not installed")
    def test_pipeline_prepares_text_for_compute(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            trajectory = root / "dump.xyz"
            trajectory.write_text(GPUMD_TEXT, encoding="utf-8")
            input_file = root / "input.in"
            input_file.write_text(
                "action = plot\n"
                f"trajectory_file = {trajectory}\n"
                "netcdf_compression_level = 0\n"
                "netcdf_batch_size = 64\n",
                encoding="utf-8",
            )

            params = read_input(str(input_file))
            step_prepare_trajectory(params)

            self.assertEqual(params.source_format, "gpumd_xyz")
            self.assertTrue(Path(params.trajectory_path).is_file())
            self.assertEqual(
                Path(params.trajectory_path).name,
                "dump.xyz.mdtrace.nc",
            )
            from netCDF4 import Dataset
            with Dataset(params.trajectory_path, "r") as dataset:
                self.assertFalse(
                    dataset.variables["coordinates"].filters()["zlib"]
                )
                self.assertEqual(dataset.mdtrace_compression_level, 0)

            cached_params = read_input(str(input_file))
            cached_params.trajectory_file = params.trajectory_path
            step_prepare_trajectory(cached_params)
            self.assertEqual(cached_params.source_format, "gpumd_xyz")
            self.assertEqual(
                cached_params.trajectory_path,
                params.trajectory_path,
            )

    @unittest.skipUnless(NETCDF4_AVAILABLE, "netCDF4 is not installed")
    def test_pipeline_reads_gpumd_netcdf_directly(self) -> None:
        from netCDF4 import Dataset

        with TemporaryDirectory() as directory:
            root = Path(directory)
            trajectory = root / "movie.nc"
            with Dataset(
                str(trajectory),
                "w",
                format="NETCDF3_64BIT_OFFSET",
            ) as dataset:
                dataset.program = "GPUMD"
                dataset.createDimension("frame", 1)
                dataset.createDimension("atom", 1)
                dataset.createDimension("spatial", 3)
                coordinates = dataset.createVariable(
                    "coordinates",
                    "f4",
                    ("frame", "atom", "spatial"),
                )
                coordinates.units = "angstrom"
                coordinates[:] = [[[0, 0, 0]]]

            input_file = root / "input.in"
            input_file.write_text(
                "action = plot\n"
                f"trajectory_file = {trajectory}\n",
                encoding="utf-8",
            )

            params = read_input(str(input_file))
            step_prepare_trajectory(params)

            self.assertEqual(params.source_format, "gpumd_netcdf")
            self.assertEqual(params.trajectory_path, str(trajectory))
            self.assertFalse((root / "movie.nc.mdtrace.nc").exists())


if __name__ == "__main__":
    unittest.main()
