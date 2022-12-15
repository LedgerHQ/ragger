from dataclasses import dataclass
from pathlib import Path

import pytest

from ragger.firmware import Firmware
from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend


@dataclass(frozen=True)
class Application:
    path: Path
    firmware: Firmware


ELF_DIRECTORY = Path(__file__).parent / 'elfs'

BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

APPLICATIONS = [
    Application(ELF_DIRECTORY / 'boilerplate_nanos.elf', Firmware('nanos', '2.1')),
    Application(ELF_DIRECTORY / 'boilerplate_nanox.elf', Firmware('nanox', '2.0.2')),
    Application(ELF_DIRECTORY / 'boilerplate_nanosp.elf', Firmware('nanosp', '1.0.3'))
]


def pytest_addoption(parser):
    parser.addoption("--backend", action="store", default="speculos")


@pytest.fixture(params=APPLICATIONS)
def application(request):
    return request.param


@pytest.fixture(scope="session")
def backend(pytestconfig):
    return pytestconfig.getoption("backend")


def create_backend(backend: str, application: Application):
    if backend.lower() == "ledgercomm":
        return LedgerCommBackend(application.firmware, interface="hid")
    elif backend.lower() == "ledgerwallet":
        return LedgerWalletBackend(application.firmware)
    elif backend.lower() == "speculos":
        assert application.path.is_file(), f"'{application.path}' elf must exist"
        return SpeculosBackend(application.path, application.firmware)
    else:
        raise ValueError(f"Backend '{backend}' is unknown. Valid backends are: {BACKENDS}")


@pytest.fixture
def client(backend, application):
    with create_backend(backend, application) as b:
        yield b


@pytest.fixture(autouse=True)
def use_only_on_backend(request, backend):
    if request.node.get_closest_marker('use_on_backend'):
        current_backend = request.node.get_closest_marker('use_on_backend').args[0]
        if current_backend != backend:
            pytest.skip(f'skipped on this backend: "{current_backend}"')


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "use_only_on_backend(backend): skip test if not on the specified backend",
    )
