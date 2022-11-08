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
from io import BytesIO
from pathlib import Path
from PIL import Image
from typing import Optional, Generator

from speculos.client import SpeculosClient, screenshot_equal, ApduResponse, ApduException

from ragger import logger
from ragger.error import ExceptionRAPDU
from ragger.firmware import Firmware
from ragger.utils import RAPDU, Crop
from .interface import BackendInterface


def raise_policy_enforcer(function):

    def decoration(self: 'SpeculosBackend', *args, **kwargs) -> RAPDU:
        # Catch backend raise
        try:
            rapdu: RAPDU = function(self, *args, **kwargs)
        except ApduException as error:
            rapdu = RAPDU(error.sw, error.data)

        logger.debug("Receiving '%s'", rapdu)

        if self.is_raise_required(rapdu):
            raise ExceptionRAPDU(rapdu.status, rapdu.data)
        else:
            return rapdu

    return decoration


class SpeculosBackend(BackendInterface):

    _ARGS_KEY = 'args'

    def __init__(self,
                 application: Path,
                 firmware: Firmware,
                 host: str = "127.0.0.1",
                 port: int = 5000,
                 **kwargs):
        super().__init__(firmware)
        self._host = host
        self._port = port
        args = ["--model", firmware.device, "--sdk", firmware.version]
        if self._ARGS_KEY in kwargs:
            assert isinstance(kwargs[self._ARGS_KEY], list), \
                f"'{self._ARGS_KEY}' ({kwargs[self._ARGS_KEY]}) keyword " \
                "argument  must be a list of arguments"
            kwargs[self._ARGS_KEY].extend(args)
        else:
            kwargs[self._ARGS_KEY] = args
        self._client: SpeculosClient = SpeculosClient(app=str(application),
                                                      api_url=self.url,
                                                      **kwargs)
        self._pending: Optional[ApduResponse] = None

    @property
    def url(self) -> str:
        return f"http://{self._host}:{self._port}"

    def __enter__(self) -> "SpeculosBackend":
        logger.info(f"Starting {self.__class__.__name__} stream")
        self._client.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._client.__exit__(*args, **kwargs)

    def send_raw(self, data: bytes = b"") -> None:
        logger.debug("Sending '%s'", data.hex())
        self._pending = ApduResponse(self._client._apdu_exchange_nowait(data))

    @raise_policy_enforcer
    def receive(self) -> RAPDU:
        assert self._pending is not None
        result = RAPDU(0x9000, self._pending.receive())
        return result

    @raise_policy_enforcer
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        logger.debug("Sending '%s'", data.hex())
        return RAPDU(0x9000, self._client._apdu_exchange(data))

    @raise_policy_enforcer
    def _get_last_async_response(self, response) -> RAPDU:
        return RAPDU(0x9000, response.receive())

    @contextmanager
    def exchange_async_raw(self, data: bytes = b"") -> Generator[None, None, None]:
        with self._client.apdu_exchange_nowait(cla=data[0],
                                               ins=data[1],
                                               p1=data[2],
                                               p2=data[3],
                                               data=data[5:]) as response:
            yield
            self._last_async_response = self._get_last_async_response(response)

    def right_click(self) -> None:
        self._client.press_and_release("right")

    def left_click(self) -> None:
        self._client.press_and_release("left")

    def both_click(self) -> None:
        self._client.press_and_release("both")

    def compare_screen_with_snapshot(self, snap_path: Path, crop: Optional[Crop] = None) -> bool:
        snap = BytesIO(self._client.get_screenshot())
        if crop is not None:
            return screenshot_equal(f"{snap_path}",
                                    snap,
                                    left=crop.left,
                                    upper=crop.upper,
                                    right=crop.right,
                                    lower=crop.lower)
        else:
            return screenshot_equal(f"{snap_path}", snap)

    def save_screen_snapshot(self, path: Path) -> None:
        screenshot = self._client.get_screenshot()
        snap = Image.open(BytesIO(screenshot))
        snap.save(path)
