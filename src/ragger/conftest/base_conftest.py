import pytest
from typing import Optional
from pathlib import Path
from ragger.firmware import Firmware
from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend
from ragger.navigator import NanoNavigator, StaxNavigator
from ragger.utils import find_project_root_dir
from ragger.logger import get_default_logger

from ragger.conftest import configuration as conf

BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

DEVICES = ["nanos", "nanox", "nanosp", "stax", "all"]

FIRMWARES = [
    Firmware('nanos', '2.1'),
    Firmware('nanox', '2.0.2'),
    Firmware('nanosp', '1.0.4'),
    Firmware('stax', '1.0'),
]


def pytest_addoption(parser):
    parser.addoption("--device", choices=DEVICES, required=True)
    parser.addoption("--backend", choices=BACKENDS, default="speculos")
    parser.addoption("--display", action="store_true", default=False)
    parser.addoption("--golden_run", action="store_true", default=False)
    parser.addoption("--log_apdu_file", action="store", default=None)


@pytest.fixture(scope="session")
def backend_name(pytestconfig):
    return pytestconfig.getoption("backend")


@pytest.fixture(scope="session")
def display(pytestconfig):
    return pytestconfig.getoption("display")


@pytest.fixture(scope="session")
def golden_run(pytestconfig):
    return pytestconfig.getoption("golden_run")


@pytest.fixture(scope="session")
def log_apdu_file(pytestconfig):
    filename = pytestconfig.getoption("log_apdu_file")
    return Path(filename).resolve() if filename is not None else None


@pytest.fixture(scope="session")
def root_pytest_dir(request):
    return Path(request.config.rootdir).resolve()


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

        device = metafunc.config.getoption("device")
        backend_name = metafunc.config.getoption("backend")

        if device == "all":
            if backend_name != "speculos":
                raise ValueError("Invalid device parameter on this backend")

            # Add all supported firmwares
            for fw in FIRMWARES:
                fw_list.append(fw)
                ids.append(fw.device + " " + fw.version)

        else:
            # Enable firmware for demanded device
            for fw in FIRMWARES:
                if device == fw.device:
                    fw_list.append(fw)
                    ids.append(fw.device + " " + fw.version)

        metafunc.parametrize("firmware", fw_list, ids=ids, scope="session")


def prepare_speculos_args(root_pytest_dir: Path, firmware: Firmware, display: bool):
    speculos_args = []

    if display:
        speculos_args += ["--display", "qt"]

    device = firmware.device
    if device == "nanosp":
        device = "nanos2"

    # Find the compiled application for the requested device
    project_root_dir = find_project_root_dir(root_pytest_dir)

    app_path = Path(project_root_dir / "build" / device / "bin" / "app.elf").resolve()
    if not app_path.is_file():
        raise ValueError(f"File '{app_path}' missing. Did you compile for this target?")

    if not len(conf.OPTIONAL["SIDELOADED_APPS"]) == 0:
        if conf.OPTIONAL["SIDELOADED_APPS_DIR"] == "":
            raise ValueError("Configuration \"SIDELOADED_APPS_DIR\" is mandatory if \
                             \"SIDELOADED_APPS\" is used")
        libs_dir = Path(project_root_dir / conf.OPTIONAL["SIDELOADED_APPS_DIR"]).resolve()
        if not libs_dir.is_dir():
            raise ValueError(f"Sideloaded apps directory '{libs_dir}' missing. \
                             Did you gather the elfs?")

        # Add "-l Appname:filepath" to Speculos command line for every required lib app
        for file_name, lib_name in conf.OPTIONAL["SIDELOADED_APPS"].items():
            lib_path = Path(libs_dir / file_name / device / "bin/app.elf").resolve()
            if not lib_path.is_file():
                raise ValueError(f"File '{lib_path}' missing. Did you compile for this target?")
            speculos_args.append(f"-l{lib_name}:{lib_path}")

    return (app_path, {"args": speculos_args})


# Depending on the "--backend" option value, a different backend is
# instantiated, and the tests will either run on Speculos or on a physical
# device depending on the backend
def create_backend(root_pytest_dir: Path, backend_name: str, firmware: Firmware, display: bool,
                   log_apdu_file: Optional[Path]):
    if backend_name.lower() == "ledgercomm":
        return LedgerCommBackend(firmware=firmware, interface="hid", log_apdu_file=log_apdu_file)
    elif backend_name.lower() == "ledgerwallet":
        return LedgerWalletBackend(firmware=firmware, log_apdu_file=log_apdu_file)
    elif backend_name.lower() == "speculos":
        app_path, speculos_args = prepare_speculos_args(root_pytest_dir, firmware, display)
        return SpeculosBackend(app_path,
                               firmware=firmware,
                               log_apdu_file=log_apdu_file,
                               **speculos_args)
    else:
        raise ValueError(f"Backend '{backend_name}' is unknown. Valid backends are: {BACKENDS}")


# Backend scope can be configured by the user
@pytest.fixture(scope=conf.OPTIONAL["BACKEND_SCOPE"])
def backend(root_pytest_dir, backend_name, firmware, display, log_apdu_file):
    with create_backend(root_pytest_dir, backend_name, firmware, display, log_apdu_file) as b:
        yield b


@pytest.fixture
def navigator(backend, firmware, golden_run):
    if firmware.device.startswith("nano"):
        return NanoNavigator(backend, firmware, golden_run)
    elif firmware.device.startswith("stax"):
        return StaxNavigator(backend, firmware, golden_run)
    else:
        raise ValueError(f"Device '{firmware.device}' is unsupported.")


@pytest.fixture
def use_only_on_backend(request, backend_name):
    if request.node.get_closest_marker('use_on_backend'):
        current_backend = request.node.get_closest_marker('use_on_backend').args[0]
        if current_backend != backend_name:
            pytest.skip(f'skipped on this backend: "{current_backend}"')


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "use_only_on_backend(backend): skip test if not on the specified backend",
    )


def log_full_conf():
    logger = get_default_logger()
    logger.debug("Running Ragger with the following conf:")
    for key, value in conf.REQUIRED.items():
        logger.debug(f"    {key} = '{value}'")
    for key, value in conf.OPTIONAL.items():
        logger.debug(f"    {key} = '{value}'")


def assert_full_conf():
    missing = []
    for key, value in conf.REQUIRED.items():
        if value == "":
            missing.append(key)
    if missing:
        raise ValueError(f"Missing required conf parameters: '{missing}")


# RUN ON IMPORT
log_full_conf()
assert_full_conf()
