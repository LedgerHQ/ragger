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
from typing import Optional, Sequence, Union

import bip_utils as bu

from .utils import BIP

I32_LAST_BIT_MASK = 0b01111111111111111111111111111111


# Bip44 format: m / purpose' / coin_type' / account' / change / address_index
class ExtendedBip32Path(bu.Bip32Path):
    Bip32PathArgs = Sequence[Union[int, bu.bip.bip32.bip32_key_data.Bip32KeyIndex]]

    def __init__(self, elems: Optional[Union[bytes, Bip32PathArgs]] = None):
        if not elems:
            raise ValueError("A Bip32 path can't be empty")
        if isinstance(elems, bytes):
            super().__init__((elems[i:i + 4] for i in range(0, len(elems), 4)), is_absolute=True)
        else:
            super().__init__(elems, is_absolute=True)

    @staticmethod
    def _to_int(b: bytes) -> int:
        return int.from_bytes(b, 'big')

    @property
    def purpose(self) -> BIP:
        return BIP(self._to_int(self[0]) & I32_LAST_BIT_MASK)

    @property
    def coin_type(self) -> int:
        return self._to_int(self[1]) & I32_LAST_BIT_MASK

    @property
    def account(self) -> int:
        return self._to_int(self[2]) & I32_LAST_BIT_MASK

    @property
    def change(self) -> int:
        return self._to_int(self[3])

    @property
    def address_index(self) -> int:
        return self._to_int(self[4])
