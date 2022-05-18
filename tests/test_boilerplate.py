from requests.exceptions import ConnectionError

import pytest

from ragger import ApduException, RAPDU
from ragger.backend import SpeculosBackend


def test_error_returns_not_raises(client_no_raise):
    result = client_no_raise.exchange(0x01, 0x00)
    assert isinstance(result, RAPDU)
    assert result.status == 0x6e00
    assert not result.data


def test_error_raises_not_returns(client):
    try:
        client.exchange(0x01, 0x00)
    except ApduException as e:
        assert e.sw == 0x6e00
        assert not e.data


@pytest.mark.use_on_backend("speculos")
def test_quit_app(client, application):
    right_clicks = {
        'nanos': 3,
        'nanox': 3,
        'nanosp': 3
    }
    for _ in range(right_clicks[application.firmware.device]):
        client.right_click()

    with pytest.raises(ConnectionError):
        # clicking on "Quit", Speculos then stops and raises
        client.both_click()
