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
from contextlib import contextmanager
from typing import Generator

from ledgerwallet.client import LedgerClient, CommException
from speculos.client import ApduException

from ragger import logger, RAPDU, Firmware
from .interface import BackendInterface


def manage_error(function):

    def decoration(self: "LedgerWalletBackend", *args, **kwargs) -> RAPDU:
        try:
            rapdu: RAPDU = function(self, *args, **kwargs)
        except CommException as error:
            if self.raises and not self.is_valid(error.sw):
                raise ApduException(error.sw, error.data)
            rapdu = RAPDU(error.sw, error.data)
        logger.debug("Receiving '%s'", rapdu)
        return rapdu

    return decoration


class LedgerWalletBackend(BackendInterface):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __enter__(self) -> "LedgerWalletBackend":
        logger.info(f")Starting {self.__class__.__name__} stream")
        self._client = LedgerClient()
        return self

    def __exit__(self, *args, **kwargs):
        assert self._client is not None
        self._client.close()

    def send_raw(self, data: bytes = b"") -> None:
        logger.debug("Sending '%s'", data)
        assert self._client is not None
        self._client.device.write(data)

    @manage_error
    def receive(self) -> RAPDU:
        assert self._client is not None
        raw_result = self._client.device.read()
        result = RAPDU(int.from_bytes(raw_result[-2:], "big"), raw_result[:-2]
                       or b"")
        logger.debug("Receiving '%s'", result)
        return result

    @manage_error
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        logger.debug("Exchange: sending   > '%s'", data)
        assert self._client is not None
        raw_result = self._client.raw_exchange(data)
        result = RAPDU(int.from_bytes(raw_result[-2:], "big"), raw_result[:-2]
                       or b"")
        logger.debug("Exchange: receiving < '%s'", result)
        return result

    @contextmanager
    def exchange_async_raw(self,
                           data: bytes = b"") -> Generator[None, None, None]:
        self.send_raw(data)
        yield
        self._last_async_response = self.receive()

    def right_click(self) -> None:
        pass

    def left_click(self) -> None:
        pass

    def both_click(self) -> None:
        pass
