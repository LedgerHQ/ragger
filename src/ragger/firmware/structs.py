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

    def __init__(self, device: str, version: str):
        assert device.lower() in SDK_VERSIONS.keys()
        try:
            versions = SDK_VERSIONS[device.lower()]
        except KeyError:
            raise KeyError(f"Version {version} for {device} is not supported or does not exist")
        # Some versions used are not semantic, like 2.0 and such. These are managed here
        super().__init__(device.lower(), version, versions.get_last_from_string(version))
