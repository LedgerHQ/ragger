# Ragger

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
pip install --extra-index-url https://test.pypi.org/simple/ -U --no-deps .
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
import pytest
from ragger.backend import SpeculosBackend, LedgerCommBackend

# adding a pytest CLI option "--backend"
def pytest_addoption(parser):
    print(help(parser.addoption))
    parser.addoption("--backend", action="store", default="speculos")

# accessing the value of the "--backend" option as a fixture
@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")

# Depending on the "--backend" option value, a different backend is
# instantiated, and the tests will either run on Speculos or on a physical
# device depending on the backend
def create_backend(backend: bool, raises: bool = True):
    if backend.lower() == "ledgercomm":
        return LedgerCommBackend(interface="hid", raises=raises)
    elif backend.lower() == "ledgerwallet":
        return LedgerWalletBackend()
    elif backend.lower() == "speculos":
        args = ['--model', 'nanos', '--sdk', '2.1']
        return SpeculosBackend(APPLICATION, args=args, raises=raises)
    else:
        raise ValueError(f"Backend '{backend}' is unknown. Valid backends are: {BACKENDS}")
```

The `client` fixture can be used to discuss with the instantiated backend.
Its interface is documented [here](src/ragger/backend/interface.py).

The test suite is then launched:

```
pytest <tests/path>                                               # by default, will run tests on the Speculos emulator
pytest --backend [speculos|ledgercomm|ledgerwallet] <tests/path>  # will run tests on the selected backend
```

You can try the tests of this very repository with the boilerplate application
on a NanoS.
