from typing import Dict, Any

# The following parameters, if any, are required.
# Please set their values in your 'conftest.py' file
REQUIRED_CONFIGURATION: Dict[str, Any] = {
}

# The following parameters are optional and can be used to customize your tests
# You can set their values in your 'conftest.py' file if you want to use them
OPTIONAL_CONFIGURATION: Dict[str, Any] = {

    # use this parameter if you want Speculos to emulate other applications being installed on the device
    # example: {"bitcoin": "Bitcoin", "ethereum": "Ethereum"}
    "SIDELOADED_APPS": {},

    # Mandatory in case SIDELOADED_APPS is used
    "SIDELOADED_APPS_DIR": "",

    # As the backend instantiation may take some time, Ragger supports multiple backend scopes.
    # You can choose to share the backend instance between {session / module / class / function}
    # When using "session" all your tests will share a single backend instance (faster)
    # When using "function" each test will have its independent backend instance (no collusion)
    "BACKEND_SCOPE": "class"
}
