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
from pathlib import Path
from typing import Optional, Generator

from ledgercomm import Transport

from ragger import logger, RAPDU, Firmware, Crop
from ragger.error import ExceptionRAPDU
from .interface import BackendInterface


def raise_policy_enforcer(function):

    def decoration(self: 'LedgerCommBackend', *args, **kwargs) -> RAPDU:
        rapdu: RAPDU = function(self, *args, **kwargs)

        logger.debug("Receiving '%s'", rapdu)

        if self.is_raise_required(rapdu):
            raise ExceptionRAPDU(rapdu.status, rapdu.data)
        else:
            return rapdu

    return decoration


class LedgerCommBackend(BackendInterface):

    def __init__(self,
                 firmware: Firmware,
                 host: str = "127.0.0.1",
                 port: int = 9999,
                 interface: str = 'hid',
                 *args,
                 **kwargs):
        super().__init__(firmware)
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

    @raise_policy_enforcer
    def receive(self) -> RAPDU:
        assert self._client is not None
        result = RAPDU(*self._client.recv())
        logger.debug("Receiving '%s'", result)
        return result

    @raise_policy_enforcer
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        logger.debug("Exchange: sending   > '%s'", data)
        assert self._client is not None
        result = RAPDU(*self._client.exchange_raw(data))
        logger.debug("Exchange: receiving < '%s'", result)
        return result

    @contextmanager
    def exchange_async_raw(self, data: bytes = b"") -> Generator[None, None, None]:
        self.send_raw(data)
        yield
        self._last_async_response = self.receive()

    def right_click(self) -> None:
        pass

    def left_click(self) -> None:
        pass

    def both_click(self) -> None:
        pass

    def navigate_until_snap(self,
                            path: Path,
                            test_case_name: Path,
                            start_img_idx: int = 0,
                            last_img_idx: int = 0,
                            take_snaps: bool = True,
                            timeout: int = 30,
                            crop_first: Crop = None,
                            crop_last: Crop = None) -> int:
        pass

    def navigate_and_compare_until_snap(self,
                                        path: Path,
                                        test_case_name: Path,
                                        start_img_idx: int = 0,
                                        last_img_idx: int = 0) -> bool:
        pass
