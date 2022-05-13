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
from typing import Optional, Iterable, Generator

from ledgercomm import Transport
from speculos.client import ApduException

from ragger import logger
from .interface import BackendInterface, RAPDU


def manage_error(function):

    def decoration(self: 'LedgerCommBackend', *args, **kwargs) -> RAPDU:
        rapdu: RAPDU = function(self, *args, **kwargs)
        logger.debug("Receiving '%s'", rapdu)
        if not self.raises or self.is_valid(rapdu.status):
            return rapdu
        # else should raise
        raise ApduException(rapdu.status, rapdu.data)

    return decoration


class LedgerCommBackend(BackendInterface):

    def __init__(self,
                 host: str = "127.0.0.1",
                 port: int = 9999,
                 raises: bool = False,
                 interface: str = 'hid',
                 valid_statuses: Iterable[int] = (0x9000, ),
                 *args,
                 **kwargs):
        super().__init__(raises=raises, valid_statuses=valid_statuses)
        self._host = host
        self._port = port
        self._client: Optional[Transport] = None
        kwargs['interface'] = interface
        self._args = (args, kwargs)

    def __enter__(self) -> "LedgerCommBackend":
        logger.info(f"Starting {self.__class__.__name__} stream")
        self._client = Transport(server=self._host,
                                 port=self._port,
                                 *self._args[0],
                                 **self._args[1])
        return self

    def __exit__(self, *args, **kwargs):
        assert self._client is not None
        self._client.close()

    def send_raw(self, data: bytes = b"") -> None:
        logger.debug("Sending '%s'", data)
        assert self._client is not None
        self._client.send_raw(data)

    @manage_error
    def receive(self) -> RAPDU:
        assert self._client is not None
        result = RAPDU(*self._client.recv())
        logger.debug("Receiving '%s'", result)
        return result

    @manage_error
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        logger.debug("Exchange: sending   > '%s'", data)
        assert self._client is not None
        result = RAPDU(*self._client.exchange_raw(data))
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
