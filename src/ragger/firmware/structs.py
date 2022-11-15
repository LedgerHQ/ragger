"""
   Copyright 2022 Ledger SAS

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from dataclasses import dataclass

from semver import VersionInfo

from .versions import SDK_VERSIONS


@dataclass(frozen=True)
class _Firmware:
    device: str
    version: str
    semantic_version: VersionInfo


class Firmware(_Firmware):
    """
    The Firmware container class holds information on the expected device on which
    the current Ragger code will apply on.

    It is composed of:

    - a `device` type, which represents the name of the physical device
      ('nanos', 'nanox', ...),
    - a `version`, which represent the SDK version associated with the physical
      device.

    A third attribute is also generated: `semantic_version`, which is deduced
    from the `version` by the `VersionManager` class, by selecting the latest
    `semantic_version` matching the given `version`. For instance, NanoS 2.1
    will fallback to version 2.1.0.
    """

    def __init__(self, device: str, version: str):
        assert device.lower() in SDK_VERSIONS.keys()
        try:
            versions = SDK_VERSIONS[device.lower()]
        except KeyError:
            raise KeyError(f"Version {version} for {device} is not supported or does not exist")
        # Some versions used are not semantic, like 2.0 and such. These are managed here
        super().__init__(device.lower(), version, versions.get_last_from_string(version))
