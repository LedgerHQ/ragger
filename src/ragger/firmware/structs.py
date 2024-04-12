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
from enum import IntEnum, auto


class Firmware(IntEnum):
    NANOS = auto()
    NANOSP = auto()
    NANOX = auto()
    STAX = auto()
    FLEX = auto()

    @property
    def device(self) -> str:
        """
        A proxy property for :attr:`.Firmware.name`.
        This property is deprecated. It is advise to not use it.
        """
        return self.name

    @property
    def name(self) -> str:
        """
        Returns the name of the current firmware's device
        """
        return super().name.lower()

    @property
    def is_nano(self):
        """
        States if the firmware's name starts with 'nano' or not.
        """
        return self.name.startswith("nano")
