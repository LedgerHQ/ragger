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
from enum import Enum
from typing import Dict, Optional, Type

from semver import VersionInfo


class VersionManager(Enum):
    """
    A class managing the versions of a specific device.

    Any class deriving from :class:`VersionManager` declares its managed
    versions as class attributes (it is an :class:`Enum`). This attributes must
    be of type :class:`semver.ServerInfo`. Class methods helps getting specific
    managed versions::

      class Versions(VersionManager):
          Version1 = semver.VersionInfo(1, 4, 0)
          Version2 = semver.VersionInfo(2, 0, 3)

      Versions.get_last()         # returns semver.VersionInfo(2, 0, 3)
      Versions.get_last(major=1)  # returns semver.VersionInfo(1, 4, 0)
    """

    @classmethod
    def get_last(cls,
                 major: Optional[int] = None,
                 minor: Optional[int] = None,
                 patch: Optional[int] = None,
                 *args) -> VersionInfo:
        """
        Returns the :class:`semver.VersionInfo` matching the given version
        numbers. If the version numbers are incomplete, fallbacks to the latest
        version matching the given numbers.

        For instance, if the enum contains version ``2.0.1`` and ``2.0.4``,
        ``VersionManager.get_last(major=2, minor=0)`` will return the ``2.0.4``
        version.

        If a number is given, its higher-level numbers are required: patch needs
        major and minor, and minor needs major (else the function raises a
        ``ValueError``).

        If no suitable version are found, raises a ``ValueError``.

        :param major: The major version in semantic versioning
        :type major: int
        :param minor: The minor version in semantic versioning
        :type minor: int
        :param patch: The patch version in semantic versioning
        :type patch: int
        :return: The latest matching version
        :rtype: :class:`semver.VersionInfo`
        """
        # error cases: (None, 2) or (1, None, 4) or (None, 2, 2)
        if (minor is not None and major is None):
            raise ValueError("Minor version can not be pinned if major is not")
        if (patch is not None and (major is None or minor is None)):
            raise ValueError("Patch version can not be pinned if major AND minor are not")
        try:
            if major is None:
                message = str()
                return max(v.value for v in cls)
            if major is not None and minor is None:
                message = f"{major} "
                return max(v.value for v in cls if v.value.major == major)
            if major is not None and minor is not None and patch is None:
                message = f"{major}.{minor} "
                return max(v.value for v in cls
                           if (v.value.major == major and v.value.minor == minor))
            message = f"{major}.{minor}.{patch} "
            return max(
                v.value for v in cls
                if (v.value.major == major and v.value.minor == minor and v.value.patch == patch))
        except ValueError:
            raise ValueError(f"No version {message}found")

    @classmethod
    def get_last_from_string(cls, version: str) -> VersionInfo:
        """
        Returns the :class:`semver.VersionInfo` matching the given version
        string. If the version string is incomplete, fallbacks to the latest
        version matching the version string.

        For instance, if the enum contains version ``2.0.1`` and ``2.0.4``,
        ``VersionManager.get_last_from_string("2.0")`` will return the ``2.0.4``
        version.

        Version strings must be valid semantic version string, or at least
        two-digits strings (like "2.0"). A version of "2" will raise.

        If no suitable version are found, raises a ``ValueError``.

        :param version: The version
        :type version: str
        :return: The latest matching version
        :rtype: :class:`semver.VersionInfo`
        """
        # special case: version with 2 numbers like "2.0"
        if version.count(".") == 1:
            return cls.get_last(*(int(v) for v in version.split(".")))
        return cls.get_last(*VersionInfo.parse(version))


class NanoSVersions(VersionManager):
    V_1_6_1 = VersionInfo(1, 6, 1)
    V_2_0_0 = VersionInfo(2, 0, 0)
    V_2_1_0 = VersionInfo(2, 1, 0)


class NanoSPVersions(VersionManager):
    V_1_0_1 = VersionInfo(1, 0, 1)
    V_1_0_2 = VersionInfo(1, 0, 2)
    V_1_0_3 = VersionInfo(1, 0, 3)
    V_1_0_4 = VersionInfo(1, 0, 4)


class NanoXVersions(VersionManager):
    V_1_3_0 = VersionInfo(1, 3, 0)
    V_2_0_0 = VersionInfo(2, 0, 0)
    V_2_0_1 = VersionInfo(2, 0, 1)
    V_2_0_2 = VersionInfo(2, 0, 2)


class StaxVersions(VersionManager):
    V_1_0_0 = VersionInfo(1, 0, 0)


#: This global holds the currently supported device names and related SDK
#: versions. Managed devices are currently: "nanos", "nanosp" and  "nanox"
SDK_VERSIONS: Dict[str, Type[VersionManager]] = {
    "nanos": NanoSVersions,
    "nanosp": NanoSPVersions,
    "nanox": NanoXVersions,
    "stax": StaxVersions,
}
