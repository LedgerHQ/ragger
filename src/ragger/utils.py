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
from struct import pack
from typing import List

SUPPORTED_DEVICES: List[str] = ["nanos", "nanox", "nanosp"]


@dataclass(frozen=True)
class Firmware:
    device: str
    version: str

    def __init__(self, device: str, version: str):
        assert device.lower() in SUPPORTED_DEVICES
        object.__setattr__(self, "device", device.lower())
        object.__setattr__(self, "version", version)


@dataclass(frozen=True)
class RAPDU:
    status: int
    data: bytes

    def __str__(self):
        return f'[0x{self.status:02x}] {self.data.hex() if self.data else "<Nothing>"}'


def pack_APDU(cla: int,
              ins: int,
              p1: int = 0,
              p2: int = 0,
              data: bytes = b"") -> bytes:
    return pack(">BBBBB", cla, ins, p1, p2, len(data)) + data
