import pytest
from typing import Optional
from pathlib import Path
from ragger.firmware import Firmware
from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend
from ragger.navigator import NanoNavigator
from ragger.utils import app_path_from_app_name


# Adapt this path to your application root directory
APP_ROOT_DIR = (Path(__file__).parent.parent.parent).resolve()

# Adapt this name part of the compiled app <name>_<device>.elf in the APPS_DIRECTORY
APP_NAME = "MyAPP"

BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

FIRMWARES = [Firmware('nanos', '2.1'),
             Firmware('nanox', '2.0.2'),
             Firmware('nanosp', '1.0.3')]


def pytest_addoption(parser):
    parser.addoption("--backend", action="store", default="speculos")
    parser.addoption("--display", action="store_true", default=False)
    parser.addoption("--elfs_dir", action="store", default="bin")
    parser.addoption("--golden_run", action="store_true", default=False)
    parser.addoption("--log_apdu_file", action="store", default=None)
    # Enable using --'device' in the pytest command line to restrict testing to specific devices
    for fw in FIRMWARES:
        parser.addoption("--"+fw.device, action="store_true", help=f"run on {fw.device} only")
    parser.addoption("--all", action="store_true", help="run on all devices")


@pytest.fixture(scope="session")
def backend_name(pytestconfig):
    return pytestconfig.getoption("backend")


@pytest.fixture(scope="session")
def display(pytestconfig):
    return pytestconfig.getoption("display")


@pytest.fixture(scope="session")
def elfs_dir(pytestconfig):
    return pytestconfig.getoption("elfs_dir")


@pytest.fixture(scope="session")
def golden_run(pytestconfig):
    return pytestconfig.getoption("golden_run")


@pytest.fixture(scope="session")
def log_apdu_file(pytestconfig):
    filename = pytestconfig.getoption("log_apdu_file")
    return Path(filename).resolve() if filename is not None else None


@pytest.fixture
def test_name(request):
    # Get the name of current pytest test
    test_name = request.node.name

    # Remove firmware suffix:
    # -  test_xxx_transaction_ok[nanox 2.0.2]
    # => test_xxx_transaction_ok
    return test_name.split("[")[0]


# Glue to call every test that depends on the firmware once for each required firmware
def pytest_generate_tests(metafunc):
    if "firmware" in metafunc.fixturenames:
        fw_list = []
        ids = []

        # If "all" was specified, run on all firmwares
        if metafunc.config.getoption("all"):
            for fw in FIRMWARES:
                fw_list.append(fw)
                ids.append(fw.device + " " + fw.version)

        else:
            # Enable only demanded firmwares
            for fw in FIRMWARES:
                if metafunc.config.getoption(fw.device):
                    fw_list.append(fw)
                    ids.append(fw.device + " " + fw.version)

        if not fw_list:
            raise ValueError(f"No device specified")

        metafunc.parametrize("firmware", fw_list, ids=ids, scope="session")


def prepare_speculos_args(firmware: Firmware, display: bool, elfs_dir: str):
    speculos_args = []

    if display:
        speculos_args += ["--display", "qt"]

    if elfs_dir == "bin":
        app_path = APP_ROOT_DIR / elfs_dir / "app.elf"
        assert app_path.is_file(), f"{app_path} must exist"
    else:
        app_path = app_path_from_app_name(APP_ROOT_DIR / elfs_dir, APP_NAME, firmware.device)

    return ([app_path], {"args": speculos_args})


# Depending on the "--backend" option value, a different backend is
# instantiated, and the tests will either run on Speculos or on a physical
# device depending on the backend
def create_backend(backend_name: str, firmware: Firmware, display: bool, elfs_dir: str, log_apdu_file: Optional[Path]):
    if backend_name.lower() == "ledgercomm":
        return LedgerCommBackend(firmware=firmware, interface="hid", log_apdu_file=log_apdu_file)
    elif backend_name.lower() == "ledgerwallet":
        return LedgerWalletBackend(firmware=firmware, log_apdu_file=log_apdu_file)
    elif backend_name.lower() == "speculos":
        args, kwargs = prepare_speculos_args(firmware, display, elfs_dir)
        return SpeculosBackend(*args, firmware=firmware, log_apdu_file=log_apdu_file, **kwargs)
    else:
        raise ValueError(f"Backend '{backend_name}' is unknown. Valid backends are: {BACKENDS}")


# This fixture will return the properly configured backend, to be used in tests.
# If your tests needs to be run on independent Speculos instances (in case they affect
# setting for example), then you should change this fixture scope.
@pytest.fixture(scope="session")
def backend(backend_name, firmware, display, elfs_dir, log_apdu_file):
    with create_backend(backend_name, firmware, display, elfs_dir, log_apdu_file) as b:
        yield b


@pytest.fixture(scope="session")
def navigator(backend, firmware, golden_run):
    if firmware.device.startswith("nano"):
        return NanoNavigator(backend, firmware, golden_run)
    else:
        raise ValueError(f"Device '{firmware.device}' is unsupported.")


@pytest.fixture(autouse=True)
def use_only_on_backend(request, backend):
    if request.node.get_closest_marker('use_on_backend'):
        current_backend = request.node.get_closest_marker('use_on_backend').args[0]
        if current_backend != backend:
            pytest.skip(f'skipped on this backend: "{current_backend}"')


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "use_only_on_backend(backend): skip test if not on the specified backend",
    )
