from pathlib import Path

import pytest

from ragger.backend import SpeculosBackend, RAPDU, ApduException


APPLICATION = Path(__file__).parent / 'elfs' / 'app.elf'


def test_error_returns_not_raises():
    with SpeculosBackend(APPLICATION, raises=False) as client:
        result = client.exchange(0x01, 0x00)
        assert isinstance(result, RAPDU)
        assert result.status == 0x6e00
        assert not result.data


def test_error_raises_not_returns():
    with SpeculosBackend(APPLICATION, raises=True) as client:
        try:
            client.exchange(0x01, 0x00)
        except ApduException as e:
            assert e.sw == 0x6e00
            assert not e.data
