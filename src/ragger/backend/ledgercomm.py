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

from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from time import sleep

from ledgercomm import Transport
from ledgered.devices import Device

from ragger.error import ExceptionRAPDU
from ragger.utils import RAPDU

from .physical_backend import PhysicalBackend


def raise_policy_enforcer(function):

    def decoration(self: "LedgerCommBackend", *args, **kwargs) -> RAPDU:
        rapdu: RAPDU = function(self, *args, **kwargs)

        self.apdu_logger.info("<= %s%4x", rapdu.data.hex(), rapdu.status)

        if self.is_raise_required(rapdu):
            raise ExceptionRAPDU(rapdu.status, rapdu.data)
        else:
            return rapdu

    return decoration


class LedgerCommBackend(PhysicalBackend):
    def __init__(
        self,
        device: Device,
        *args,
        host: str = "127.0.0.1",
        port: int = 9999,
        interface: str = "hid",
        log_apdu_file: Path | None = None,
        with_gui: bool = False,
        **kwargs,
    ):
        super().__init__(device, *args, log_apdu_file=log_apdu_file, with_gui=with_gui, **kwargs)
        self._host = host
        self._port = port
        self._client: Transport | None = None
        kwargs["interface"] = interface
        self._args = (args, kwargs)

    def __enter__(self) -> "LedgerCommBackend":
        self.logger.info(f"Starting {self.__class__.__name__} stream")

        try:
            self._client = Transport(*self._args[0], server=self._host, port=self._port, **self._args[1])
        except Exception:
            # Give some time for the USB stack to power up and to be enumerated
            # Might be needed in successive tests where app is exited at the end of the test
            sleep(1)
            self._client = Transport(*self._args[0], server=self._host, port=self._port, **self._args[1])
        return self

    def __exit__(self, *args):
        super().__exit__(*args)
        if self._client is None:
            raise RuntimeError("Backend not initialized: used outside context manager")
        self._client.close()

    def handle_usb_reset(self) -> None:
        self.logger.info(f"Re-starting {self.__class__.__name__} stream")
        self.__exit__()
        self.__enter__()

    def send_raw(self, data: bytes = b"") -> None:
        self.apdu_logger.info("=> %s", data.hex())
        if self._client is None:
            raise RuntimeError("Backend not initialized: used outside context manager")
        self._client.send_raw(data)

    @raise_policy_enforcer
    def receive(self) -> RAPDU:
        if self._client is None:
            raise RuntimeError("Backend not initialized: used outside context manager")
        result = RAPDU(*self._client.recv())
        return result

    @raise_policy_enforcer
    def exchange_raw(self, data: bytes = b"", tick_timeout: int = 0) -> RAPDU:
        self.apdu_logger.info("=> %s", data.hex())
        if self._client is None:
            raise RuntimeError("Backend not initialized: used outside context manager")
        result = RAPDU(*self._client.exchange_raw(data))
        return result

    @contextmanager
    def exchange_async_raw(self, data: bytes = b"") -> Generator[bool, None, None]:
        self.send_raw(data)
        yield True
        self._last_async_response = self.receive()
