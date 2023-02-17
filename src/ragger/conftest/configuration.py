from dataclasses import dataclass


@dataclass
class OptionalOptions:
    SIDELOADED_APPS: dict
    SIDELOADED_APPS_DIR: str
    BACKEND_SCOPE: str


OPTIONAL = OptionalOptions(
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
)
