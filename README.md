# Ragger

[![codecov](https://codecov.io/gh/LedgerHQ/ragger/branch/develop/graph/badge.svg)](https://codecov.io/gh/LedgerHQ/ragger)

---
**Warning**

This library contains documentation and functionalities related to Ledger Stax hardware (sometimes refered as `fatstacks`). As of the writing of the message, neither the SDK nor the Speculos support is available publicly for Ledger Stax hardware. This is therefore preventing users to use such functionalities.

---


This library aims at reducing the cost of running code on both Speculos emulator
or on a real device.

It mainly consists on an interface which is implemented by three backends:

- an emulator-only backend, `SpeculosBackend`, which uses
  [`SpeculosClient`](https://github.com/LedgerHQ/speculos/blob/master/speculos/client.py)
  to run an app on a Speculos emulator. With this backend, APDU can be send directly,
  without having to connect a device, start a docker or anything.

- two physical backends (although technically they are agnostic, but the
  `SpeculosClient` is superior with an emulator), `LedgerCommBackend` and
  `LedgewWalletbackend`, which use respectively the
  [`LedgerComm` library](https://github.com/LedgerHQ/ledgercomm) or the
  [`LedgerWallet` library](https://github.com/LedgerHQ/ledgerctl/) to discuss
  with a physical device. In these cases, the physical device must be started,
  with the expected application *installed* and *running*, and connected to the
  computer through USB.


More complete documentation can be found [here](https://ledgerhq.github.io/ragger/).


## Installation

### Python package

Ragger is currently not available on PIP repositories.

To install it, you need to run at the root of the `git` repository:

```
pip install --extra-index-url https://test.pypi.org/simple/ '.[all_backends]'
```

The extra index is important, as it brings the latest version of Speculos.

### Extras

Sometimes we just need some function embedded in the library, or just one backend. It can be
bothersome (and heavy) to import all dependencies when just one or none are needed.

This is why backends are stored as extra in `ragger`. Installing `ragger` without extra means **it
comes without any backends**.

Extra are straightforward: `[speculos]`, `[ledgercomm]` and `[ledgerwallet]`. In the previous
section, `[all_backends]` was used: it is a shortcut to `[speculos,ledgercomm,ledgerwallet]`.

### Speculos dependencies

If the Speculos extra is installed (to use the `SpeculosBackend`), system dependencies are needed.
[Check the doc](https://speculos.ledger.com/installation/build.html) for these.

## Features

The `src/ragger/backend/interface.py` file describes the methods that can be implemented by the different backends and that allow to interact with a device (either a real device or emulated):

* `send`: send a formatted APDU.
* `send_raw`: send a raw APDU.
* `receive`: receive a response ADPU.
* `exchange`: send a formatted APDU and wait for a response (synchronous).
* `exchange_raw`: send a raw APDU and wait for a response (synchronous).
* `exchange_async`: send a formatted APDU and give back the control to the caller (asynchronous).
* `exchange_async_raw`: send a raw APDU and give back the control to the caller.
* `right_click`: perform a right click on a device.
* `left_click`: perform a left click on a device.
* `both_click`: perform a click on both buttons (left + right) of a device.
* `finger_touch`: performs a finger touch on the device screen.
* `compare_screen_with_snapshot`: compare the current device screen with the provided snapshot.

The `src/ragger/navigator/navigator.py` file describes the methods that can be implemented by the different device navigators and that allow to interact with an emulated device:
* `navigate`: navigate on the device according to a set of navigation instructions provided.
* `navigate_and_compare`: navigate on the device according to a set of navigation instructions provided then compare each step screenshot with "golden images".
* `navigate_until_snap`: navigate on the device until a snapshot is found and then validate.
* `navigate_until_text`: navigate on the device until a text string is found on screen and then validate.
* `navigate_until_text_and_compare`: same as `navigate_until_text` but compare screenshots taken at each step with "golden images".

## Examples
### With `pytest`

The backends can be easily integrated in a `pytest` test suite with the following files:

* A `conftest.py` which can be heavily based on [this template](template/conftest.py).
* A `usage.md` which can be heavily based on [this template](template/usage.md).
* Tests files which would looks like:

```python
#---------- some_tests.py ----------

TESTS_ROOT_DIR = Path(__file__).parent


def test_something(backend, firmware):
    rapdu: RAPDU = backend.exchange(<whatever>)
    assert rapdu.status == 0x9000


def test_with_user_action_and_screenshot_comparison(backend, firmware, navigator, test_name):
    with backend.exchange_async(<whatever>)
        if firmware.device == "nanos":
            instructions = [
                NavIns(NavInsID.RIGHT_CLICK),
                NavIns(NavInsID.RIGHT_CLICK),
                NavIns(NavInsID.BOTH_CLICK),
            ]
        elif firmware.device == "stax":
            instructions = [
                    NavIns(NavInsID.USE_CASE_REVIEW_TAP),
                    NavIns(NavInsID.USE_CASE_REVIEW_TAP),
                    NavIns(NavInsID.USE_CASE_REVIEW_CONFIRM),
                    NavIns(NavInsID.USE_CASE_STATUS_WAIT)
                ]
        else:
            instructions = [
                NavIns(NavInsID.RIGHT_CLICK),
                NavIns(NavInsID.BOTH_CLICK),
            ]
        navigator.navigate_and_compare(TESTS_ROOT_DIR, test_name, instructions)
    rapdu: RAPDU = backend.last_async_response
    assert rapdu.status == 0x9000
    assert verify(rapdu.data)
```

The `backend` fixture used to discuss with the instantiated backend is documented
[here](src/ragger/backend/interface.py).

The `navigator` fixture used to navigate with the instantiated backend is documented
[here](src/ragger/navigator/navigator.py).

After implementing the tests, the test suite can be easily switched on the different backends:

```
pytest <tests/path>                                               # by default, will run tests on the Speculos emulator
pytest --backend [speculos|ledgercomm|ledgerwallet] <tests/path>  # will run tests on the selected backend
```

The tests of this repository are basically the same as this example, except
the tests run on the three current firmwares (NanoS, NanoX and NanoS+).

## Documentation

The complete documentation can be found [here](https://ledgerhq.github.io/ragger/).
If you want to generate it locally, you'll need the `doc` dependencies to
generate the documentation:

```bash
pip install .[doc]
```

You will also need the `graphviz` package in order to generate some dependency
diagrams:

```bash
apt-get install graphviz
```

Once done, you can generate the documentation:

```bash
(cd doc && make gen_resources && make html)
```
