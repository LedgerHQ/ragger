import os
import subprocess
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ragger.error import ExceptionRAPDU
from ragger.utils import misc

from ..helpers import temporary_directory


class TestMisc(TestCase):

    def test_app_path_from_app_name_ok(self):
        with temporary_directory() as dir_path:
            app_name, device = "some_name", "some_device"
            expected = (dir_path / f"{app_name}_{device}.elf")
            expected.touch()
            self.assertEqual(expected, misc.find_library_application(dir_path, app_name, device))

    def test_app_path_from_app_name_nok_no_directory(self):
        with self.assertRaises(AssertionError):
            misc.find_library_application(Path("/this/does/not/exists/"), "a", "b")

    def test_app_path_from_app_name_nok_no_file(self):
        with temporary_directory() as dir_path:
            with self.assertRaises(AssertionError):
                misc.find_library_application(dir_path, "a", "b")

    def test_find_application_ok_c(self):
        device, sdk = "device", "sdk"
        with temporary_directory() as dir_path:
            tmp_dir = (dir_path / "build" / device / "bin")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            expected = tmp_dir / "app.elf"
            expected.touch()
            result = misc.find_application(dir_path, device, sdk)
            self.assertEqual(result, expected)

    def test_find_application_ok_rust(self):
        device, sdk, appname = "device", "rust", "rustapp"
        with temporary_directory() as dir_path:
            cmd = ["cargo", "new", appname]
            subprocess.check_output(cmd, cwd=dir_path)
            app_path = dir_path / appname
            tmp_dir = (app_path / "target" / device / "release")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            expected = tmp_dir / appname
            expected.touch()
            result = misc.find_application(app_path, device, sdk)
            self.assertEqual(result, expected)

    def test_find_application_nok_not_dir(self):
        directory, device, sdk = Path("does not exist"), "device", "sdk"
        with self.assertRaises(AssertionError) as error:
            misc.find_application(directory, device, sdk)
        self.assertIn(str(directory), str(error.exception))

    def test_find_application_nok_not_file(self):
        device, sdk = "device", "sdk"
        with temporary_directory() as dir_path:
            tmp_dir = (dir_path / "build" / device / "bin")
            tmp_dir.mkdir(parents=True, exist_ok=True)
            expected = tmp_dir / "app.elf"
            with self.assertRaises(AssertionError) as error:
                misc.find_application(dir_path, device, sdk)
            self.assertIn(str(expected), str(error.exception))

    def test_find_project_root_dir_ok(self):
        with temporary_directory() as dir_path:
            os.mkdir(Path(dir_path / ".git").resolve())
            nested_dir = Path(dir_path / "subfolder").resolve()
            os.mkdir(nested_dir)
            nested_dir = Path(nested_dir / "another_subfolder").resolve()
            os.mkdir(nested_dir)
            self.assertEqual(
                Path(dir_path).resolve(),
                Path(misc.find_project_root_dir(nested_dir)).resolve())

    def test_find_project_root_dir_nok(self):
        with temporary_directory() as dir_path:
            nested_dir = Path(dir_path / "subfolder").resolve()
            os.mkdir(nested_dir)
            nested_dir = Path(nested_dir / "another_subfolder").resolve()
            os.mkdir(nested_dir)
            with self.assertRaises(ValueError):
                misc.find_project_root_dir(nested_dir)

    def test_prefix_with_len(self):
        buffer = bytes.fromhex("0123456789")
        self.assertEqual(b"\x05" + buffer, misc.prefix_with_len(buffer))

    def test_create_currency_config_no_sub(self):
        ticker = "ticker"  # size 6
        name = "name"  # size 4
        expected = b"\x06" + ticker.encode() + b"\x04" + name.encode() + b"\x00"
        self.assertEqual(expected, misc.create_currency_config(ticker, name, None))

    def test_create_currency_config_full(self):
        ticker = "ticker"  # size 6
        name = "name"  # size 4
        subconfig = ("subconfig", 13)  # size 9 + 1
        expected = b"\x06" + ticker.encode() + b"\x04" + name.encode() + b"\x0b" \
            + b"\x09" + subconfig[0].encode() + subconfig[1].to_bytes(1, byteorder="big")
        self.assertEqual(expected, misc.create_currency_config(ticker, name, subconfig))

    def test_split_message(self):
        message = b"some message to split"
        expected = [b"some ", b"messa", b"ge to", b" spli", b"t"]
        self.assertEqual(expected, misc.split_message(message, 5))

    def test_get_current_app_name_and_version_ok(self):
        name, version = "appname", "12.345.6789"
        backend = MagicMock()
        # format (=1)
        # <l1v name>
        # <l1v version>
        # <l1v flags>
        backend.exchange().data = bytes.fromhex("01") \
            + len(name.encode()).to_bytes(1, "big") + name.encode() \
            + len(version.encode()).to_bytes(1, "big") + version.encode() \
            + bytes.fromhex("0112")
        result_name, result_version = misc.get_current_app_name_and_version(backend)
        self.assertEqual(name, result_name)
        self.assertEqual(version, result_version)

    def test_get_current_app_name_and_version_nok(self):
        error_status, backend = 0x1234, MagicMock()
        backend.exchange.side_effect = ExceptionRAPDU(error_status)
        with self.assertRaises(ExceptionRAPDU) as error:
            misc.get_current_app_name_and_version(backend)
        self.assertEqual(error.exception.status, error_status)
        # specific behavior: device locked
        backend.exchange.side_effect = ExceptionRAPDU(misc.ERROR_BOLOS_DEVICE_LOCKED)
        with self.assertRaises(ValueError) as error:
            misc.get_current_app_name_and_version(backend)
        self.assertEqual(misc.ERROR_MSG_DEVICE_LOCKED, str(error.exception))

    def test_exit_current_app(self):
        backend = MagicMock()
        self.assertIsNone(misc.exit_current_app(backend))

    def test_open_app_from_dashboard_ok(self):
        backend = MagicMock()
        self.assertIsNone(misc.open_app_from_dashboard(backend, "some app"))

    def test_open_app_from_dashboard_nok(self):
        error_status, backend = 0x1234, MagicMock()
        backend.exchange.side_effect = ExceptionRAPDU(error_status)
        with self.assertRaises(ExceptionRAPDU) as error:
            misc.open_app_from_dashboard(backend, "first app")
        self.assertEqual(error.exception.status, error_status)
        # specific behavior: user refuses
        backend.exchange.side_effect = ExceptionRAPDU(misc.ERROR_DENIED_BY_USER)
        with self.assertRaises(ValueError) as error:
            misc.open_app_from_dashboard(backend, "second app")
        # specific behavior: app not installed
        backend.exchange.side_effect = ExceptionRAPDU(misc.ERROR_APP_NOT_FOUND)
        with self.assertRaises(ValueError) as error:
            misc.open_app_from_dashboard(backend, "third app")
