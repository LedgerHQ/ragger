# Ragger

[![codecov](https://codecov.io/gh/LedgerHQ/ragger/branch/develop/graph/badge.svg)](https://codecov.io/gh/LedgerHQ/ragger)

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

## Installation

### Python package

Ragger is currently not available on PIP repositories.

To install it, you need to run at the root of the `git` repository:

```
pip install --extra-index-url https://test.pypi.org/simple/ .
```

The extra index is important, as it brings the latest version of Speculos.

### Other

Speculos dependencies are obviously needed too.
[Check the doc](https://speculos.ledger.com/installation/build.html) for these.

## Examples

### With `pytest`

The backends can be easily integrated in a `pytest` test suite with the
following fixtures:

```python
---------- conftest.py ----------

import pytest
from ragger import Firmware
from ragger.backend import SpeculosBackend, LedgerCommBackend

# This variable is needed for Speculos only (physical tests need the application to be already installed)
APPLICATION = "Path/to/the/application.elf"
# This variable will be useful in tests to implement different behavior depending on the firmware
NANOS_FIRMWARE = Firmware("nanos", "2.1")

# adding a pytest CLI option "--backend"
def pytest_addoption(parser):
    print(help(parser.addoption))
    parser.addoption("--backend", action="store", default="speculos")

# accessing the value of the "--backend" option as a fixture
@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")

# Providing the firmware as a fixture
# This can be easily parametrized, which would allow to run the tests on several firmware type or version
@pytest.fixture
def firmware():
    return NANOS_FIRMWARE

# Depending on the "--backend" option value, a different backend is
# instantiated, and the tests will either run on Speculos or on a physical
# device depending on the backend
def create_backend(backend: bool, firmware):
    if backend.lower() == "ledgercomm":
        return LedgerCommBackend(firmware, interface="hid")
    elif backend.lower() == "ledgerwallet":
        return LedgerWalletBackend(firmware)
    elif backend.lower() == "speculos":
        return SpeculosBackend(APPLICATION, firmware)
    else:
        raise ValueError(f"Backend '{backend}' is unknown. Valid backends are: {BACKENDS}")

# This final fixture will return the properly configured backend client, to be used in tests
@pytest.fixture
def client(backend, firmware):
    with create_backend(backend, firmware) as b:
        yield b

---------- some_tests.py ----------

def test_something(client, firmware):
    client.exchange(<whatever>)
    if firmware.device == "nanos":
        result = <do something specific to NanoS>
    else:
        result = <do something else>
    assert result.status == 0x9000
```

The `client` fixture used to discuss with the instantiated backend is documented
[here](src/ragger/backend/interface.py).

After implementing the tests, the test suite can be easily switched on the different backends:

```
pytest <tests/path>                                               # by default, will run tests on the Speculos emulator
pytest --backend [speculos|ledgercomm|ledgerwallet] <tests/path>  # will run tests on the selected backend
```

The tests of this repository are a basically the same as this exemple, except
the tests run on the three current firmwares (NanoS, NanoX and NanoS+).
