from dataclasses import dataclass


@dataclass
class OptionalOptions:
    APP_NAME: str
    APP_DIR: str
    SIDELOADED_APPS: dict
    SIDELOADED_APPS_DIR: str
    BACKEND_SCOPE: str
    CUSTOM_SEED: str


OPTIONAL = OptionalOptions(
    # Use this parameter if you want to make sure the right app is started upon backend instantiation.
    # This is only used for LedgerWallet and LedgerComm backend.
    APP_NAME=str(),

    # Use this parameter if the app is not compiled at the project root directory.
    # This parameter will indicate the subdirectory where Speculos will search the "build/" directory
    # example: "." or "app/"
    APP_DIR=".",

    # use this parameter if you want Speculos to emulate other applications being installed on the device
    # example: {"bitcoin": "Bitcoin", "ethereum": "Ethereum"}
    # this would result in Speculos being launched with -lbitcoin:/path/to/bitcoin_device.elf
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
