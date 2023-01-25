import pytest
from contextlib import contextmanager
from pathlib import Path
from ragger.utils import misc


class TestMisc():

    def test_find_project_root_dir_ok(self, root_pytest_dir):
        assert root_pytest_dir.parent == misc.find_project_root_dir(Path(__file__).parent)

    def test_find_project_root_dir_nok(self):
        with pytest.raises(ValueError):
            misc.find_project_root_dir(Path("/this/does/not/exists/"))

    def test_prefix_with_len(self):
        buffer = bytes.fromhex("0123456789")
        assert b"\x05" + buffer == misc.prefix_with_len(buffer)

    def test_create_currency_config_no_sub(self):
        ticker = "ticker"  # size 6
        name = "name"  # size 4
        expected = b"\x06" + ticker.encode() + b"\x04" + name.encode() + b"\x00"
        assert expected == misc.create_currency_config(ticker, name, None)

    def test_create_currency_config_full(self):
        ticker = "ticker"  # size 6
        name = "name"  # size 4
        subconfig = ("subconfig", 13)  # size 9 + 1
        expected = b"\x06" + ticker.encode() + b"\x04" + name.encode() + b"\x0b" \
            + b"\x09" + subconfig[0].encode() + subconfig[1].to_bytes(1, byteorder="big")
        assert expected == misc.create_currency_config(ticker, name, subconfig)

    def test_split_message(self):
        message = b"some message to split"
        expected = [b"some ", b"messa", b"ge to", b" spli", b"t"]
        assert expected == misc.split_message(message, 5)
