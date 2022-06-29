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
