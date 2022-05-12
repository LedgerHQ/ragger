from pathlib import Path

import pytest

from ragger.backend import SpeculosBackend, LedgerCommBackend


APPLICATION = Path(__file__).parent / 'elfs' / 'app.elf'


def pytest_addoption(parser):
    parser.addoption("--live", action="store_true", default=False)


@pytest.fixture(scope="session")
def live(pytestconfig):
    return pytestconfig.getoption("live")


def create_backend(live: bool, raises: bool = True):
    if live:
        backend = LedgerCommBackend(interface="hid", raises=raises)
    else:
        args = ['--model', 'nanos', '--sdk', '2.1']
        backend = SpeculosBackend(APPLICATION, args=args, raises=raises)
    return backend


@pytest.fixture
def client(live):
    with create_backend(live) as b:
        yield b


@pytest.fixture
def client_no_raise(live):
    with create_backend(live, raises=False) as b:
        yield b
