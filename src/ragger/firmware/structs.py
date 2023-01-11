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

    It is composed of three attributes:

    - ``device`` (``str``), which represents the name of the physical device
      ('nanos', 'nanox', ...),
    - ``version`` (``str``), which represent the SDK version associated with the
      physical device.
    - ``semantic_version`` (:class:`semver.VersionInfo`), which is deduced from
      ``device`` and ``version``. ``device`` is used to get the correct
      :class:`VersionManager <ragger.firmware.versions.VersionManager>` class
      from the :data:`SDK_VERSIONS <ragger.firmware.versions.SDK_VERSIONS>`
      global, then the :class:`semver.VersionInfo` is selected according to the
      given ``version``. For instance, ``device = "NanoS"`` and
      ``version =  "2.1"`` will results into
      ``semantic_version = semver.VersionInfo(2, 1, 0)``.
    """

    def __init__(self, device: str, version: str):
        """
        Instantiate the :class:`Firmware`.

        If ``device`` does not match any device declared in
        :data:`SDK_VERSIONS <ragger.firmware.versions.SDK_VERSIONS>`, will raise
        a ``KeyError``.

        If ``version`` does not match any version in the
        :class:`VersionManager <ragger.firmware.versions.VersionManager>`
        related to the ``SDK_VERSION[device]``, will raise a ``ValueError``.
        """
        try:
            versions = SDK_VERSIONS[device.lower()]
        except KeyError:
            raise KeyError(f"Version {version} for {device} is not supported or does not exist")
        # Some versions used are not semantic, like 2.0 and such. These are managed here
        super().__init__(device.lower(), version, versions.get_last_from_string(version))

    @property
    def has_bagl(self):
        return self.device.lower().startswith("nano")

    @property
    def has_nbgl(self):
        return self.device.lower().startswith("stax")
