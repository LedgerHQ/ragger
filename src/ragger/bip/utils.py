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
from enum import IntEnum
from typing import Union

import bip_utils as bu


class BIP(IntEnum):
    BIP44 = 0x2c
    BIP49 = 0x31
    BIP84 = 0x54
    BIP86 = 0x56


BIPS_KEY = Union[bu.Bip44, bu.Bip49, bu.Bip84, bu.Bip86]
BIPS_COIN = Union[bu.Bip44Coins, bu.Bip49Coins, bu.Bip84Coins, bu.Bip86Coins]
