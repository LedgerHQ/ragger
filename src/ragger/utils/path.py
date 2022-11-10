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
from bip32 import HARDENED_INDEX
from enum import IntEnum


class BtcDerivationPathFormat(IntEnum):
    LEGACY = 0x00
    P2SH = 0x01
    BECH32 = 0x02
    CASHADDR = 0x03  # Deprecated
    BECH32M = 0x04


def pack_derivation_path(derivation_path: str) -> bytes:
    split = derivation_path.split("/")
    first = split.pop(0)
    assert first == "m", "master expected"
    path_bytes: bytes = (len(split)).to_bytes(1, byteorder='big')
    for i in split:
        if (i[-1] == "'"):
            path_bytes += (int(i[:-1]) | HARDENED_INDEX).to_bytes(4, byteorder='big')
        else:
            path_bytes += int(i).to_bytes(4, byteorder='big')
    return path_bytes


def bitcoin_pack_derivation_path(format: BtcDerivationPathFormat, derivation_path: str) -> bytes:
    assert isinstance(format, BtcDerivationPathFormat)
    return format.to_bytes(1, "big") + pack_derivation_path(derivation_path)
