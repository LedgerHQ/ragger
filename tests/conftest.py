from pathlib import Path

import pytest

from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend


BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]
APPLICATION = Path(__file__).parent / 'elfs' / 'app.elf'


def pytest_addoption(parser):
    print(help(parser.addoption))
    parser.addoption("--backend", action="store", default="speculos")


@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")


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


@pytest.fixture
def client(backend):
    with create_backend(backend) as b:
        yield b


@pytest.fixture
def client_no_raise(backend):
    with create_backend(backend, raises=False) as b:
        yield b


@pytest.fixture(autouse=True)
def use_only_on_backend(request, backend):
    if request.node.get_closest_marker('use_on_backend'):
        current_backend = request.node.get_closest_marker('use_on_backend').args[0]
        if current_backend != backend:
            pytest.skip('skipped on this backend: {}'.format(current_backend))

def pytest_configure(config):
  config.addinivalue_line(
        "markers", "use_only_on_backend(backend): skip test if not on the specified backend",
  )
