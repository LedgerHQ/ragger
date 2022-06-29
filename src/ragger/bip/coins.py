from dataclasses import dataclass
from functools import partial
from typing import Callable, Dict, Union

import bip_utils as bu

from .utils import BIP, BIPS_KEY, BIPS_COIN


@dataclass
class BUContainer:
    key_cls: BIPS_KEY
    coin: BIPS_COIN


@dataclass
class Coin:
    bips: Dict[BIP, BUContainer]
    encodings: Union[Callable, Dict[str, Callable]]

    @staticmethod
    def from_type(coin_type: int) -> "Coin":
        try:
            return COINS[coin_type]
        except KeyError:
            raise ValueError(f"Coin type '{coin_type}' is not supported")


Bitcoin = Coin(
    {
        BIP.BIP44: BUContainer(bu.Bip44, bu.Bip44Coins.BITCOIN),
        BIP.BIP49: BUContainer(bu.Bip49, bu.Bip49Coins.BITCOIN),
        BIP.BIP84: BUContainer(bu.Bip84, bu.Bip84Coins.BITCOIN),
        BIP.BIP86: BUContainer(bu.Bip86, bu.Bip86Coins.BITCOIN)
    }, {
        "p2pkh": partial(bu.P2PKHAddrEncoder.EncodeKey, net_ver=b"\x00"),
        "p2sh": partial(bu.P2SHAddrEncoder.EncodeKey, net_ver=b"\x05"),
        "bech32": partial(bu.P2WPKHAddr.EncodeKey, hrp="bc"),
    })
BitcoinTestnet = Coin(
    {
        BIP.BIP44: BUContainer(bu.Bip44, bu.Bip44Coins.BITCOIN),
        BIP.BIP49: BUContainer(bu.Bip49, bu.Bip49Coins.BITCOIN),
        BIP.BIP84: BUContainer(bu.Bip84, bu.Bip84Coins.BITCOIN),
        BIP.BIP86: BUContainer(bu.Bip86, bu.Bip86Coins.BITCOIN)
    }, {
        "p2pkh": partial(bu.P2PKHAddrEncoder.EncodeKey, net_ver=b"\x6F"),
        "p2sh": partial(bu.P2SHAddrEncoder.EncodeKey, net_ver=b"\xC4"),
        "bech32": partial(bu.P2WPKHAddr.EncodeKey, hrp="tb"),
    })
Litecoin = Coin(
    {
        BIP.BIP44: BUContainer(bu.Bip44, bu.Bip44Coins.LITECOIN),
        BIP.BIP49: BUContainer(bu.Bip49, bu.Bip49Coins.LITECOIN),
        BIP.BIP84: BUContainer(bu.Bip84, bu.Bip84Coins.LITECOIN)
    },
    {
        # legacy prefixes mirroring Bitcoin's are not used
        "p2pkh": partial(bu.P2PKHAddrEncoder.EncodeKey, net_ver=b"\x30"),
        "p2sh": partial(bu.P2SHAddrEncoder.EncodeKey, net_ver=b"\x32"),
        "bech32": partial(bu.P2WPKHAddr.EncodeKey, hrp="ltc"),
    })
Ethereum = Coin({BIP.BIP44: BUContainer(bu.Bip44, bu.Bip44Coins.ETHEREUM)},
                bu.EthAddrEncoder.EncodeKey)

COINS = {
    0x00: Bitcoin,
    0x01: BitcoinTestnet,
    0x02: Litecoin,
    0x3c: Ethereum,
}
