from requests.exceptions import ConnectionError

import pytest

from ragger import ExceptionRAPDU, RAPDU
from ragger.backend.interface import RaisePolicy


def test_error_returns_not_raises(client):
    client.set_raise_policy(RaisePolicy.RAISE_NOTHING)
    result = client.exchange(0x01, 0x00)
    assert isinstance(result, RAPDU)
    assert result.status == 0x6e00
    assert not result.data


def test_error_raises_not_returns(client):
    try:
        client.exchange(0x01, 0x00)
    except ExceptionRAPDU as e:
        assert e.status == 0x6e00
        assert not e.data


@pytest.mark.use_on_backend("speculos")
def test_quit_app(client, application):
    right_clicks = {'nanos': 3, 'nanox': 3, 'nanosp': 3}
    for _ in range(right_clicks[application.firmware.device]):
        client.right_click()

    with pytest.raises(ConnectionError):
        # clicking on "Quit", Speculos then stops and raises
        client.both_click()
