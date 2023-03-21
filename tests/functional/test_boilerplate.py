from requests.exceptions import ConnectionError

import pytest
import time

from ragger.error import ExceptionRAPDU
from ragger.utils import RAPDU
from ragger.backend import RaisePolicy
from ragger.navigator import NavInsID


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
def test_quit_app(backend, firmware, navigator):
    if firmware.device.startswith("nano"):
        right_clicks = {'nanos': 3, 'nanox': 3, 'nanosp': 3}
        backend.get_current_screen_content()

        for _ in range(right_clicks[firmware.device]):
            backend.right_click()
            backend.wait_for_screen_change()

        with pytest.raises(ConnectionError):
            # clicking on "Quit", Speculos then stops
            backend.both_click()
            time.sleep(1)

            # Then a new dummy click should raise a ConnectionError
            backend.right_click()

    else:
        backend.get_current_screen_content()

        with pytest.raises(ConnectionError):
            # clicking on "Quit", Speculos then stops and raises
            navigator.navigate([NavInsID.USE_CASE_HOME_QUIT],
                               screen_change_before_first_instruction=False,
                               screen_change_after_last_instruction=False)
            time.sleep(1)

            # Then a new dummy touch should raise a ConnectionError
            backend.finger_touch()
