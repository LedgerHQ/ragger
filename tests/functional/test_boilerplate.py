from requests.exceptions import ConnectionError

import pytest

from ragger.error import ExceptionRAPDU
from ragger.utils import RAPDU
from ragger.backend import RaisePolicy


def test_error_returns_not_raises(backend):
    backend.raise_policy = RaisePolicy.RAISE_NOTHING
    result = backend.exchange(0x01, 0x00)
    assert isinstance(result, RAPDU)
    assert result.status == 0x6e00
    assert not result.data


def test_error_raises_not_returns(backend):
    try:
        backend.exchange(0x01, 0x00)
    except ExceptionRAPDU as e:
        assert e.status == 0x6e00
        assert not e.data


@pytest.mark.use_on_backend("speculos")
def test_quit_app(backend, firmware):
    right_clicks = {'nanos': 3, 'nanox': 3, 'nanosp': 3}
    for _ in range(right_clicks[firmware.device]):
        backend.right_click()

    with pytest.raises(ConnectionError):
        # clicking on "Quit", Speculos then stops and raises
        backend.both_click()
