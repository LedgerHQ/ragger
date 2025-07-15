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
