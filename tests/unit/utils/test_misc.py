from contextlib import contextmanager
from pathlib import Path
from tempfile import mkdtemp
from unittest import TestCase

from ragger.utils import misc


class TestMisc(TestCase):

    @contextmanager
    def directory(self):
        dir_path = Path(mkdtemp())
        yield dir_path
        for filee in dir_path.iterdir():
            filee.unlink()
        dir_path.rmdir()

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
