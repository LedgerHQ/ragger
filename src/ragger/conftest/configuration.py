from dataclasses import dataclass


@dataclass
class OptionalOptions:
    APP_NAME: str
    APP_DIR: str
    LOAD_MAIN_APP_AS_LIBRARY: bool
    SIDELOADED_APPS: dict
    SIDELOADED_APPS_DIR: str
    BACKEND_SCOPE: str
    CUSTOM_SEED: str


OPTIONAL = OptionalOptions(
    # Use this parameter if you want to make sure the right app is started upon backend instantiation.
    # This is only used for LedgerWallet and LedgerComm backend.
    APP_NAME=str(),

    # Use this parameter to point to the repository holding the build output of the app
    # As this parameter defaults to the base project root, it can be omitted in most cases
    # Use cases : your app is not stored at the project root dir, or you are using LOAD_MAIN_APP_AS_LIBRARY
    # example: "./app/"
    APP_DIR=".",

    # Set True if the app being tested with Ragger should be loaded as a library and not as a standalone app
    # If using this mode, use APP_DIR to set the path of the standalone app that will use the tested library
    # Useful for Ethereum plugins, for example
    LOAD_MAIN_APP_AS_LIBRARY=False,

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
)
