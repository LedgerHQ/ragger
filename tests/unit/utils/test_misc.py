import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase
from ragger.utils import misc


def rmdir(directory):
    directory = Path(directory)
    for item in directory.iterdir():
        if item.is_dir():
            rmdir(item)
        else:
            item.unlink()
    directory.rmdir()


class TestMisc(TestCase):

    @contextmanager
    def directory(self):
        dir_path = Path(mkdtemp())
        yield dir_path
        rmdir(dir_path)

    def test_app_path_from_app_name_ok(self):
        with self.directory() as dir_path:
            app_name, device = "some_name", "some_device"
            expected = (dir_path / f"{app_name}_{device}.elf")
            expected.touch()
            self.assertEqual(expected, misc.app_path_from_app_name(dir_path, app_name, device))

    def test_app_path_from_app_name_nok_no_directory(self):
        with self.assertRaises(AssertionError):
            misc.app_path_from_app_name(Path("/this/does/not/exists/"), "a", "b")

    def test_app_path_from_app_name_nok_no_file(self):
        with self.directory() as dir_path:
            with self.assertRaises(AssertionError):
                misc.app_path_from_app_name(dir_path, "a", "b")

    def test_find_project_root_dir_ok(self):
        with self.directory() as dir_path:
            os.mkdir(Path(dir_path / ".git").resolve())
            nested_dir = Path(dir_path / "subfolder").resolve()
            os.mkdir(nested_dir)
            nested_dir = Path(nested_dir / "another_subfolder").resolve()
            os.mkdir(nested_dir)
            self.assertEqual(
                Path(dir_path).resolve(),
                Path(misc.find_project_root_dir(nested_dir)).resolve())

    def test_find_project_root_dir_nok(self):
        with self.directory() as dir_path:
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
