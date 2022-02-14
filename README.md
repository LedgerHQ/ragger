# Ragger

This library aims at reducing the cost of running code on both Speculos emulator
or on a real device.

It mainly consists on an interface which is implemented in two backends:

- `SpeculosBackend`, which uses `SpeculosClient` to run code on a Speculos
  emulator. With this backend, APDU can be send directly, without having to
  start a docker or anything.

- `LedgerCommbackend`, which uses the `LedgerComm` library to discuss with a
  physical device. In this case, the physical device must be started, with the
  expected application installed and running, and connected to the computer
  through USB.


## Example

This backend can be easily integrated in a `pytest` test suite with the
following fixtures:

```python
import pytest
from ragger import SpeculosBackend, LedgerCommBackend

# adding an pytest CLI option "--live"
def pytest_addoption(parser):
    parser.addoption("--live", action="store_true", default=False)

# accessing the value of the "--live" option
@pytest.fixture(scope="session")
def live(pytestconfig):
    return pytestconfig.getoption("live")

# Depending on the "--live" option value, a different backend is instantiated,
# and the tests will either run on Speculos or on a physical device
@pytest.fixture(scope="session")
def client(live):
    if live:
        backend = LedgerCommBackend(interface="hid", raises=True)
    else:
        app = SCRIPT_DIR.parent.parent / "bin" / "app.elf"
        args = ['--model', 'nanos', '--sdk', '2.1']
        backend = SpeculosBackend(app, args=args, raises=True)
    with backend as b:
        yield b
```

The `client` fixture can be used to discuss with the instantiated backend.
Its interface is documented [here](src/ragger/interface.py).

The test suite is then launched:

```
pytest <tests/path>         # will run tests on Speculos emulator

pytest --live <tests/path>  # will run tests on a physical device
```