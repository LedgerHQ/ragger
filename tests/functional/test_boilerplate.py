from requests.exceptions import ConnectionError

import pytest
import time
from pathlib import Path

from ragger.error import ExceptionRAPDU
from ragger.utils import RAPDU
from ragger.backend import RaisePolicy
from ragger.navigator import NavInsID, NavIns

ROOT_SCREENSHOT_PATH = Path(__file__).parent.parent.resolve()


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
def test_quit_app(backend, device, navigator):
    if not device.touchable:
        right_clicks = {'nanos': 3, 'nanox': 3, 'nanosp': 3}
        backend.get_current_screen_content()

        for _ in range(right_clicks[device.name]):
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


@pytest.mark.use_on_backend("speculos")
def test_waiting_screen(backend, device, navigator):
    if not device.touchable:
        pytest.skip("Don't apply")

    prep_tx_apdu = bytes.fromhex("e006008015058000002c800000008000"
                                 "00000000000000000000")

    sign_tx_apdu = bytes.fromhex("e0060100310000000000000001de0b29"
                                 "5669a9fd93d5f28d9ec85e40f4cb697b"
                                 "ae000000000000029a0c466f72207520"
                                 "457468446576")

    # Test multiple way to wait for the return for the Home screen after a review.

    # Using USE_CASE_STATUS_DISMISS instruction
    backend.exchange_raw(prep_tx_apdu)
    with backend.exchange_async_raw(sign_tx_apdu):
        navigator.navigate_until_text_and_compare(
            NavInsID.USE_CASE_REVIEW_NEXT,
            [NavInsID.USE_CASE_REVIEW_CONFIRM, NavInsID.USE_CASE_STATUS_DISMISS], "Hold to sign",
            ROOT_SCREENSHOT_PATH, "waiting_screen")

    # Using WAIT_FOR_HOME_SCREEN instruction
    backend.exchange_raw(prep_tx_apdu)
    with backend.exchange_async_raw(sign_tx_apdu):
        navigator.navigate_until_text_and_compare(
            NavInsID.USE_CASE_REVIEW_NEXT,
            [NavInsID.USE_CASE_REVIEW_CONFIRM, NavInsID.WAIT_FOR_HOME_SCREEN], "Hold to sign",
            ROOT_SCREENSHOT_PATH, "waiting_screen")

    # Using WAIT_FOR_TEXT_ON_SCREEN instruction
    backend.exchange_raw(prep_tx_apdu)
    with backend.exchange_async_raw(sign_tx_apdu):
        navigator.navigate_until_text_and_compare(NavInsID.USE_CASE_REVIEW_NEXT, [
            NavInsID.USE_CASE_REVIEW_CONFIRM,
            NavIns(NavInsID.WAIT_FOR_TEXT_ON_SCREEN, ("This app enables signing", ))
        ], "Hold to sign", ROOT_SCREENSHOT_PATH, "waiting_screen")

    # Using WAIT_FOR_TEXT_NOT_ON_SCREEN instruction
    backend.exchange_raw(prep_tx_apdu)
    with backend.exchange_async_raw(sign_tx_apdu):
        navigator.navigate_until_text_and_compare(NavInsID.USE_CASE_REVIEW_NEXT, [
            NavInsID.USE_CASE_REVIEW_CONFIRM,
            NavIns(NavInsID.WAIT_FOR_TEXT_NOT_ON_SCREEN, ("Transaction", ))
        ], "Hold to sign", ROOT_SCREENSHOT_PATH, "waiting_screen")

    # Verify the error flow of WAIT_FOR_TEXT_ON_SCREEN instruction
    backend.exchange_raw(prep_tx_apdu)
    with backend.exchange_async_raw(sign_tx_apdu):
        with pytest.raises(TimeoutError) as error:
            navigator.navigate_until_text_and_compare(NavInsID.USE_CASE_REVIEW_NEXT, [
                NavInsID.USE_CASE_REVIEW_CONFIRM,
                NavIns(NavInsID.WAIT_FOR_TEXT_ON_SCREEN, ("WILL NOT BE FOUND", ))
            ], "Hold to sign", ROOT_SCREENSHOT_PATH, "waiting_screen")
    assert "Timeout waiting for screen change" in str(error.value)

    # Verify the error flow of WAIT_FOR_TEXT_ON_SCREEN instruction
    backend.exchange_raw(prep_tx_apdu)
    with backend.exchange_async_raw(sign_tx_apdu):
        with pytest.raises(TimeoutError) as error:
            navigator.navigate_until_text_and_compare(NavInsID.USE_CASE_REVIEW_NEXT, [
                NavInsID.USE_CASE_REVIEW_CONFIRM,
                NavIns(NavInsID.WAIT_FOR_TEXT_NOT_ON_SCREEN, ("T", ))
            ], "Hold to sign", ROOT_SCREENSHOT_PATH, "waiting_screen")
    assert "Timeout waiting for screen change" in str(error.value)
