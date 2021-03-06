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
from typing import Union

import bip_utils as bu

from ragger import logger
from .coins import Coin
from .path import ExtendedBip32Path

BIP44_CHANGE = {0x00: bu.Bip44Changes.CHAIN_EXT, 0x01: bu.Bip44Changes.CHAIN_INT}


class Seed:

    def __init__(self, seed: bytes):
        self._seed = seed

    @property
    def seed(self) -> bytes:
        return self._seed

    @staticmethod
    def _to_change(b: int) -> bu.Bip44Changes:
        try:
            return BIP44_CHANGE[b]
        except KeyError:
            raise ValueError(f"Change '{b}' is currently unknown.")

    @staticmethod
    def from_mnemonic(mnemonic: str) -> "Seed":
        return Seed(bu.Bip39SeedGenerator(mnemonic).Generate())

    def get_pubkey(self, path: Union[bytes, ExtendedBip32Path]) -> bytes:
        if isinstance(path, bytes):
            path = ExtendedBip32Path(path)
        key = None
        coin = None
        if path.Length() < 2:
            raise ValueError("Path is too short (needs at least 3 elements).")
        coin = Coin.from_type(path.coin_type)
        bip = coin.bips[path.purpose]
        key = bip.key_cls.FromSeed(self.seed, bip.coin).Purpose().Coin()
        if path.Length() >= 3:
            key = key.Account(path.account)
        if path.Length() >= 4:
            key = key.Change(self._to_change(path.change))
        if path.Length() >= 5:
            key = key.AddressIndex(path.address_index)
        return key.PublicKey().RawUncompressed().ToBytes()

    def get_address(self,
                    path: Union[bytes, ExtendedBip32Path],
                    *args,
                    encoding=None,
                    **kwargs) -> bytes:
        if isinstance(path, bytes):
            path = ExtendedBip32Path(path)
        pubkey = self.get_pubkey(path)

        encoding_func = lambda x: x  # noqa
        if path.Length() >= 2:
            coin = Coin.from_type(path.coin_type)
            try:
                if isinstance(coin.encodings, dict):
                    encoding_func = coin.encodings[encoding]
                else:
                    encoding_func = coin.encodings
            except KeyError:
                msg = f"No encoder named '{encoding}' found for coin {coin}. "
                msg += "Falling back to default (neutral encoder)"
                logger.warning(msg)
        return encoding_func(pubkey, *args, **kwargs)
