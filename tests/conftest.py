from dataclasses import dataclass
from pathlib import Path

import pytest

from ragger import Firmware
from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend


@dataclass(frozen=True)
class Application:
    path: Path
    firmware: Firmware

ELF_DIRECTORY = Path(__file__).parent / 'elfs'

BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

APPLICATIONS = [
    Application(ELF_DIRECTORY / 'nanos.elf', Firmware('nanos', '2.1')),
    Application(ELF_DIRECTORY / 'nanox.elf', Firmware('nanox', '2.0.2')),
    Application(ELF_DIRECTORY / 'nanosp.elf', Firmware('nanosp', '1.0'))
]


def pytest_addoption(parser):
    print(help(parser.addoption))
    parser.addoption("--backend", action="store", default="speculos")


@pytest.fixture(params=APPLICATIONS)
def application(request):
    return request.param


@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")


def create_backend(backend: bool, application: Application, raises: bool = True):
    if backend.lower() == "ledgercomm":
        return LedgerCommBackend(application.firmware, interface="hid", raises=raises)
    elif backend.lower() == "ledgerwallet":
        return LedgerWalletBackend(application.firmware)
    elif backend.lower() == "speculos":
        assert application.path.is_file(), \
            f"'{application.path}' elf must exist"
        return SpeculosBackend(
            application.path,
            application.firmware,
            raises=raises
        )
    else:
        raise ValueError(f"Backend '{backend}' is unknown. Valid backends are: {BACKENDS}")


@pytest.fixture
def client(backend, application):
    with create_backend(backend, application) as b:
        yield b


@pytest.fixture
def client_no_raise(backend, application):
    with create_backend(backend, application, raises=False) as b:
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
