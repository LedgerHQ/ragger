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
            super().__init__(bu.Bip32Path(elems[i:i + 4] for i in range(0, len(elems), 4)))
        else:
            super().__init__(elems)

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
