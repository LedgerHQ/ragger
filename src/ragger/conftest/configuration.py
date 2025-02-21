from dataclasses import dataclass
from typing import Optional, List


@dataclass
class OptionalOptions:
    APP_NAME: str
    MAIN_APP_DIR: Optional[str]
    SIDELOADED_APPS: dict
    SIDELOADED_APPS_DIR: str
    BACKEND_SCOPE: str
    CUSTOM_SEED: str
    ALLOWED_SETUPS: List[str]


OPTIONAL = OptionalOptions(
    # Use this parameter if you want to make sure the right app is started upon backend instantiation.
    # This is only used for LedgerWallet and LedgerComm backend.
    APP_NAME=str(),

    # If not None, the app being tested with Ragger should be loaded as a library and not as a standalone
    # app. This parameter points to the repository holding the "main app", i.e the app started by the
    # backend, which will then use the "local app" as a library.
    # Use cases : your app is an Ethereum plugin, which will be used as a library by the Ethereum app.
    # MAIN_APP_DIR contains the directory where the Ethereum app binaries are stored.
    # example: "./tests/"
    MAIN_APP_DIR=None,

    # use this parameter if you want Speculos to sideload libraries being installed on the device
    # Useful for Ethereum main app and exchange app, for example
    # example: {"bitcoin": "Bitcoin", "ethereum": "Ethereum"}
    # this would result in Speculos being launched with -lbitcoin:/path/to/bitcoin_device.elf
    # Mutually exclusive with LOAD_MAIN_APP_AS_LIBRARY
    SIDELOADED_APPS=dict(),

    # Mandatory in case SIDELOADED_APPS is used
    # Relative path to the directory that will store your libs, from the top repository of your application
    # example: "test/lib_binaries/"
    # place your compiled application inside with naming "name_device.elf"
    SIDELOADED_APPS_DIR=str(),

    # As the backend instantiation may take some time, Ragger supports multiple backend scopes.
    # You can choose to share the backend instance between {session / module / class / function}
    # When using "session" all your tests will share a single backend instance (faster)
    # When using "function" each test will have its independent backend instance (no collusion)
    BACKEND_SCOPE="class",

    # Use this parameter if you want speculos to use a custom seed instead of the default one.
    # This would result in speculos being launched with --seed <CUSTOM_SEED>
    # If a seed is provided through the "--seed" pytest command line option, it will override this one.
    CUSTOM_SEED=str(),

    # Use this parameter if you want ragger to handle running different test suites depending on setup
    # Useful when some tests need certain build options and other tests need other build options, or a
    # different Speculos command line
    # Adding a setup <name> will allow you to decorate your tests with it using the following syntax
    # @pytest.mark.needs_setup('<name>')
    # And run marked tests and only them using the --setup <name>
    #
    # "default" setup is always allowed, all tests without explicit decoration depend on default
    # and the --setup option defaults to "default"
    ALLOWED_SETUPS=["default"],
)
