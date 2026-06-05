import os
from dataclasses import dataclass
from ledgered.devices import DeviceType, Devices
from pathlib import Path
from typing import Tuple
from unittest import TestCase
from unittest.mock import patch

from ragger.conftest import base_conftest as bc

from ..helpers import temporary_directory


def prepare_base_dir(directory: Path) -> Tuple[Path, Path]:
    (directory / ".git").mkdir()
    (directory / "build" / "stax" / "bin").mkdir(parents=True, exist_ok=True)
    (directory / "deps" / "dep" / "build" / "stax" / "bin").mkdir(parents=True, exist_ok=True)
    dep_path = (directory / "deps" / "dep" / "build" / "stax" / "bin" / "app.elf")
    dep_path.touch()
    token_file_path = (directory / "deps" / ".ethereum_application_build_goes_there")
    token_file_path.touch()
    app_path = (directory / "build" / "stax" / "bin" / "app.elf")
    app_path.touch()
    return app_path, dep_path


@dataclass
class AppMock:
    build_directory: str
    sdk: str


@dataclass
class ManifestMock:
    app: AppMock

    @staticmethod
    def from_path(*args):
        return ManifestMock(AppMock(".", "c"))


class TestBaseConftest(TestCase):

    def setUp(self):
        self.seed = "some seed"
        self.stax = Devices.get_by_type(DeviceType.STAX)

    def test_prepare_speculos_args_simplest(self):
        with temporary_directory() as temp_dir:
            app_path, _ = prepare_base_dir(temp_dir)
            with patch("ragger.conftest.base_conftest.Manifest", ManifestMock):
                result_app, result_args = bc.prepare_speculos_args(temp_dir, self.stax, False,
                                                                   False, self.seed, [])
            self.assertEqual(result_app, app_path)
            self.assertEqual(result_args, {"args": ["--seed", self.seed]})

    def test_prepare_speculos_args_with_prod_pki(self):
        with temporary_directory() as temp_dir:
            app_path, _ = prepare_base_dir(temp_dir)
            with patch("ragger.conftest.base_conftest.Manifest", ManifestMock):
                result_app, result_args = bc.prepare_speculos_args(temp_dir, self.stax, False, True,
                                                                   self.seed, [])
            self.assertEqual(result_app, app_path)
            self.assertEqual(result_args, {"args": ["-p", "--seed", self.seed]})

    def test_prepare_speculos_args_with_custom_args(self):
        arg = "whatever"
        with temporary_directory() as temp_dir:
            app_path, _ = prepare_base_dir(temp_dir)
            with patch("ragger.conftest.base_conftest.Manifest", ManifestMock):
                result_app, result_args = bc.prepare_speculos_args(temp_dir, self.stax, False,
                                                                   False, self.seed, [arg])
            self.assertEqual(result_app, app_path)
            self.assertEqual(result_args, {"args": [arg, "--seed", self.seed]})

    def test_prepare_speculos_args_simple_with_gui(self):
        with temporary_directory() as temp_dir:
            app_path, _ = prepare_base_dir(temp_dir)
            with patch("ragger.conftest.base_conftest.Manifest", ManifestMock):
                result_app, result_args = bc.prepare_speculos_args(temp_dir, self.stax, True, False,
                                                                   self.seed, [])
            self.assertEqual(result_app, app_path)
            self.assertEqual(result_args, {"args": ["--display", "qt", "--seed", self.seed]})

    def test_prepare_speculos_args_main_as_library(self):
        with temporary_directory() as temp_dir:
            app_path, dep_path = prepare_base_dir(temp_dir)
            with patch("ragger.conftest.base_conftest.conf.OPTIONAL.MAIN_APP_DIR", "./deps"):
                with patch("ragger.conftest.base_conftest.Manifest", ManifestMock) as manifest:
                    result_app, result_args = bc.prepare_speculos_args(
                        temp_dir, self.stax, False, False, self.seed, [])
            self.assertEqual(result_app, dep_path)
            self.assertEqual(result_args, {"args": [f"-l{app_path}", "--seed", self.seed]})

    def test_prepare_speculos_args_sideloaded_apps_ok(self):
        with temporary_directory() as temp_dir:
            app_path, _ = prepare_base_dir(temp_dir)
            sideloaded_apps_dir = temp_dir / "here"
            lib1_path = sideloaded_apps_dir / "lib1/build/stax/bin/"
            lib2_path = sideloaded_apps_dir / "lib2/build/stax/bin/"
            os.makedirs(lib1_path)
            os.makedirs(lib2_path)
            lib1_exe = lib1_path / "app.elf"
            lib2_exe = lib2_path / "app.elf"
            lib1_exe.touch()
            lib2_exe.touch()

            with patch("ragger.conftest.base_conftest.conf.OPTIONAL.SIDELOADED_APPS_DIR",
                       sideloaded_apps_dir):

                with patch("ragger.conftest.base_conftest.Manifest", ManifestMock):
                    result_app, result_args = bc.prepare_speculos_args(
                        temp_dir, self.stax, False, False, self.seed, [])
                self.assertEqual(result_app, app_path)
                self.assertEqual(result_args,
                                 {"args": [f"-l{lib1_exe}", f"-l{lib2_exe}", "--seed", self.seed]})

    def test_create_backend_nok(self):
        with self.assertRaises(ValueError):
            bc.create_backend(None, "does not exist", None, None, None, None, None, [])

    def test_create_backend_speculos(self):
        with patch("ragger.conftest.base_conftest.SpeculosBackend") as backend:
            with temporary_directory() as temp_dir:
                prepare_base_dir(temp_dir)
                with patch("ragger.conftest.base_conftest.Manifest", ManifestMock):
                    result = bc.create_backend(temp_dir, "Speculos", self.stax, False, False, None,
                                               self.seed, [])
                self.assertEqual(result, backend())

    def test_create_backend_ledgercomm(self):
        with patch("ragger.conftest.base_conftest.LedgerWalletBackend") as backend:
            result = bc.create_backend(None, "ledgerWALLET", self.stax, False, False, None,
                                       self.seed, [])
            self.assertEqual(result, backend())

    def test_create_backend_ledgerwallet(self):
        with patch("ragger.conftest.base_conftest.LedgerCommBackend") as backend:
            result = bc.create_backend(None, "LedgerComm", self.stax, False, False, None, self.seed,
                                       [])
            self.assertEqual(result, backend())


class NodeMock:
    """Mock for pytest node objects, providing a nodeid."""

    def __init__(self, nodeid: str):
        self.nodeid = nodeid


class TestSanitizeTestName(TestCase):

    def test_simple_name(self):
        self.assertEqual(bc._sanitize_test_name("test_foo"), "test_foo")

    def test_strips_device_from_params(self):
        result = bc._sanitize_test_name("test_foo[nanox]")
        self.assertEqual(result, "test_foo")

    def test_keeps_non_device_params(self):
        result = bc._sanitize_test_name("test_foo[swap_valid_1-nanox]")
        self.assertEqual(result, "test_foo_swap_valid_1")

    def test_multiple_params_strips_device(self):
        result = bc._sanitize_test_name("test_foo[SubCommand.SWAP-True-nanos]")
        self.assertEqual(result, "test_foo_SubCommand.SWAP_True")

    def test_special_chars_replaced(self):
        result = bc._sanitize_test_name("test_foo[a/b:c'd e]")
        self.assertEqual(result, "test_foo_a_b_cd_e")

    def test_truncation_at_100_chars(self):
        long_name = "test_" + "a" * 200
        result = bc._sanitize_test_name(long_name)
        self.assertEqual(len(result), 100)

    def test_only_device_param(self):
        result = bc._sanitize_test_name("test_quit_app[stax]")
        self.assertEqual(result, "test_quit_app")


class TestComputeApduLogPath(TestCase):

    def setUp(self):
        self.root = Path("/tmp/project")
        self.nanox = Devices.get_by_type(DeviceType.NANOX)
        self.stax = Devices.get_by_type(DeviceType.STAX)

    def test_simple_function(self):
        node = NodeMock("tests/test_foo.py::test_bar[nanox]")
        result = bc.compute_apdu_log_path(self.root, self.nanox, node)
        self.assertEqual(result,
                         self.root / "apdu_logs" / "nanox" / "tests" / "test_foo" / "test_bar.apdus")

    def test_with_class(self):
        node = NodeMock("tests/test_bitcoin.py::TestsBitcoin::test_bitcoin[swap_valid_1-nanox]")
        result = bc.compute_apdu_log_path(self.root, self.nanox, node)
        self.assertEqual(
            result,
            self.root / "apdu_logs" / "nanox" / "tests" / "test_bitcoin" / "TestsBitcoin" /
            "test_bitcoin_swap_valid_1.apdus")

    def test_no_params(self):
        node = NodeMock("test_simple.py::test_no_param")
        result = bc.compute_apdu_log_path(self.root, self.stax, node)
        self.assertEqual(result,
                         self.root / "apdu_logs" / "stax" / "test_simple" / "test_no_param.apdus")

    def test_parametrized_no_collision(self):
        """Two parametrized tests with different params must produce different paths."""
        node_a = NodeMock("tests/test_flow.py::test_order[SubCommand.SWAP-True-nanox]")
        node_b = NodeMock("tests/test_flow.py::test_order[SubCommand.SWAP-False-nanox]")
        path_a = bc.compute_apdu_log_path(self.root, self.nanox, node_a)
        path_b = bc.compute_apdu_log_path(self.root, self.nanox, node_b)
        self.assertNotEqual(path_a, path_b)
        self.assertIn("SubCommand.SWAP_True", str(path_a))
        self.assertIn("SubCommand.SWAP_False", str(path_b))

    def test_device_no_collision(self):
        """Same test on different devices must produce different paths."""
        node = NodeMock("tests/test_foo.py::test_bar[nanox]")
        path_nanox = bc.compute_apdu_log_path(self.root, self.nanox, node)

        node_stax = NodeMock("tests/test_foo.py::test_bar[stax]")
        path_stax = bc.compute_apdu_log_path(self.root, self.stax, node_stax)

        self.assertNotEqual(path_nanox, path_stax)
        self.assertIn("nanox", str(path_nanox))
        self.assertIn("stax", str(path_stax))
        # The filename part should be identical — only the device directory differs
        self.assertEqual(path_nanox.name, path_stax.name)

    def test_nested_module_path(self):
        node = NodeMock("tests/functional/backend/test_deep.py::test_func[nanos]")
        nanos = Devices.get_by_type(DeviceType.NANOS)
        result = bc.compute_apdu_log_path(self.root, nanos, node)
        self.assertEqual(
            result,
            self.root / "apdu_logs" / "nanos" / "tests" / "functional" / "backend" / "test_deep" /
            "test_func.apdus")
