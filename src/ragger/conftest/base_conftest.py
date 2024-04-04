import pytest
from typing import Optional
from pathlib import Path
from ledgered.manifest import Manifest
from ragger.firmware import Firmware
from ragger.backend import SpeculosBackend, LedgerCommBackend, LedgerWalletBackend
from ragger.navigator import NanoNavigator, TouchNavigator, NavigateWithScenario
from ragger.utils import find_project_root_dir, find_library_application, find_application
from ragger.utils.misc import get_current_app_name_and_version, exit_current_app, open_app_from_dashboard
from ragger.logger import get_default_logger
from dataclasses import fields

from . import configuration as conf

BACKENDS = ["speculos", "ledgercomm", "ledgerwallet"]

DEVICES = ["nanos", "nanox", "nanosp", "stax", "flex", "all", "all_nano"]

FIRMWARES = [
    Firmware.NANOS,
    Firmware.NANOSP,
    Firmware.NANOX,
    Firmware.STAX,
    Firmware.FLEX,
]


def pytest_addoption(parser):
    parser.addoption("--device", choices=DEVICES, required=True)
    parser.addoption("--backend", choices=BACKENDS, default="speculos")
    parser.addoption("--display",
                     action="store_true",
                     default=False,
                     help="Pops up a Qt interface displaying either the emulated device (Speculos "
                     "backend) or the expected screens and actions (physical backend)")
    parser.addoption("--golden_run",
                     action="store_true",
                     default=False,
                     help="Do not compare the snapshots during testing, but instead save the live "
                     "ones. Will only work with 'speculos' as the backend")
    parser.addoption("--log_apdu_file", action="store", default=None, help="Log the APDU in a file")
    parser.addoption("--seed", action="store", default=None, help="Set a custom seed")


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
def cli_user_seed(pytestconfig):
    return pytestconfig.getoption("seed")


@pytest.fixture(scope="session")
def root_pytest_dir(request):
    return Path(request.config.rootpath).resolve()


@pytest.fixture(autouse="session")
def default_screenshot_path(root_pytest_dir):
    # Alias reflecting the use case to avoid exposing internal helper fixtures
    return root_pytest_dir


@pytest.fixture
def test_name(request):
    # Get the name of current pytest test
    test_name = request.node.name

    # Remove firmware suffix:
    # -  test_xxx_transaction_ok[nanox]
    # => test_xxx_transaction_ok
    return test_name.split("[")[0]


# Glue to call every test that depends on the firmware once for each required firmware
def pytest_generate_tests(metafunc):
    if "firmware" in metafunc.fixturenames:
        fw_list = []
        ids = []

        device = metafunc.config.getoption("device")
        backend_name = metafunc.config.getoption("backend")

        # Enable firmware for requested devices
        for fw in FIRMWARES:
            if device == fw.name or device == "all" or (device == "all_nano" and fw.is_nano):
                fw_list.append(fw)
                ids.append(fw.name)

        if len(fw_list) > 1 and backend_name != "speculos":
            raise ValueError("Invalid device parameter on this backend")

        metafunc.parametrize("firmware", fw_list, ids=ids, scope="session")


def prepare_speculos_args(root_pytest_dir: Path, firmware: Firmware, display: bool,
                          cli_user_seed: str):
    speculos_args = []

    if display:
        speculos_args += ["--display", "qt"]

    device = firmware.name
    if device == "nanosp":
        device = "nanos2"

    # Find the project root repository
    project_root_dir = find_project_root_dir(root_pytest_dir)

    manifest = Manifest.from_path(project_root_dir / "ledger_app.toml")

    # Find the main application for the requested device
    # If the app is to be loaded as a library, the main app should be located in a subfolder of
    # project_root_dir / conf.OPTIONAL.MAIN_APP_DIR. There should be only one subfolder in the path.
    main_app_path = None
    if conf.OPTIONAL.MAIN_APP_DIR is not None:
        app_dir_content = list((project_root_dir / conf.OPTIONAL.MAIN_APP_DIR).iterdir())
        app_dir_subdirectories = [child for child in app_dir_content if child.is_dir()]
        if len(app_dir_subdirectories) != 1:
            raise ValueError(
                f"Expected a single folder in {manifest.app.build_directory}, found {len(app_dir_subdirectories)}"
            )
        main_app_path = find_application(app_dir_subdirectories[0], device, "c")
    # If the app is standalone, the main app should be located in project_root_dir / manifest.app.build_directory
    else:
        main_app_path = find_application(project_root_dir / manifest.app.build_directory, device,
                                         manifest.app.sdk)

    # Find all libraries that have to be sideloaded
    if conf.OPTIONAL.MAIN_APP_DIR is not None:
        # This repo holds the library, not the standalone app: search in root_dir/build
        lib_path = find_application(project_root_dir, device, manifest.app.sdk)
        speculos_args.append(f"-l{lib_path}")

    elif len(conf.OPTIONAL.SIDELOADED_APPS) != 0:
        # We are testing a a standalone app that needs libraries: search in SIDELOADED_APPS_DIR
        if conf.OPTIONAL.SIDELOADED_APPS_DIR == "":
            raise ValueError("Configuration \"SIDELOADED_APPS_DIR\" is mandatory if "
                             "\"SIDELOADED_APPS\" is used")
        libs_dir = Path(project_root_dir / conf.OPTIONAL.SIDELOADED_APPS_DIR)
        # Add "-l Appname:filepath" to Speculos command line for every required lib app
        for coin_name, lib_name in conf.OPTIONAL.SIDELOADED_APPS.items():
            lib_path = find_library_application(libs_dir, coin_name, device)
            speculos_args.append(f"-l{lib_name}:{lib_path}")

    # Check if custom user seed has been provided through CLI or optional configuration.
    # CLI user seed has priority over the optional configuration seed.
    if cli_user_seed:
        speculos_args += ["--seed", cli_user_seed]
    elif not len(conf.OPTIONAL.CUSTOM_SEED) == 0:
        speculos_args += ["--seed", conf.OPTIONAL.CUSTOM_SEED]

    return (main_app_path, {"args": speculos_args})


# Depending on the "--backend" option value, a different backend is
# instantiated, and the tests will either run on Speculos or on a physical
# device depending on the backend
def create_backend(root_pytest_dir: Path, backend_name: str, firmware: Firmware, display: bool,
                   log_apdu_file: Optional[Path], cli_user_seed: str):
    if backend_name.lower() == "ledgercomm":
        return LedgerCommBackend(firmware=firmware,
                                 interface="hid",
                                 log_apdu_file=log_apdu_file,
                                 with_gui=display)
    elif backend_name.lower() == "ledgerwallet":
        return LedgerWalletBackend(firmware=firmware, log_apdu_file=log_apdu_file, with_gui=display)
    elif backend_name.lower() == "speculos":
        main_app_path, speculos_args = prepare_speculos_args(root_pytest_dir, firmware, display,
                                                             cli_user_seed)
        return SpeculosBackend(main_app_path,
                               firmware=firmware,
                               log_apdu_file=log_apdu_file,
                               **speculos_args)
    else:
        raise ValueError(f"Backend '{backend_name}' is unknown. Valid backends are: {BACKENDS}")


# Backend scope can be configured by the user
@pytest.fixture(scope=conf.OPTIONAL.BACKEND_SCOPE)
def backend(root_pytest_dir, backend_name, firmware, display, log_apdu_file, cli_user_seed):
    with create_backend(root_pytest_dir, backend_name, firmware, display, log_apdu_file,
                        cli_user_seed) as b:
        if backend_name.lower() != "speculos" and conf.OPTIONAL.APP_NAME:
            # Make sure the app is restarted as this is what is requested by the fixture scope
            app_name, version = get_current_app_name_and_version(b)
            requested_app = conf.OPTIONAL.APP_NAME
            if app_name == requested_app:
                exit_current_app(b)
                b.handle_usb_reset()
            elif app_name != "BOLOS":
                raise ValueError(f"Unexpected app opened: {app_name}")
            open_app_from_dashboard(b, requested_app)
            b.handle_usb_reset()
        yield b


@pytest.fixture(scope=conf.OPTIONAL.BACKEND_SCOPE)
def navigator(backend, firmware, golden_run):
    if firmware.is_nano:
        return NanoNavigator(backend, firmware, golden_run)
    else:
        # `firmware` fixture is generated by `pytest_generate_tests`, which controls it against the
        # `FIRMWARES` list. So by design, if the firmware is not a Nano, it is either Stax or Flex
        return TouchNavigator(backend, firmware, golden_run)


@pytest.fixture(scope="function")
def scenario_navigator(navigator, firmware, test_name, default_screenshot_path):
    return NavigateWithScenario(navigator, firmware.device, test_name, default_screenshot_path)


@pytest.fixture(autouse=True)
def use_only_on_backend(request, backend_name):
    marker = request.node.get_closest_marker('use_on_backend')
    if marker:
        current_backend = marker.args[0]
        if current_backend != backend_name:
            pytest.skip(f'skipped on this backend: "{current_backend}"')


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "use_on_backend(backend): skip test if not on the specified backend",
    )


def log_full_conf():
    logger = get_default_logger()
    logger.debug("Running Ragger with the following conf:")
    for field in fields(conf.OPTIONAL):
        logger.debug(f"\t{field.name} = '{getattr(conf.OPTIONAL, field.name)}'")


# RUN ON IMPORT
log_full_conf()
