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
from time import time, sleep
from json import dumps

from speculos.client import SpeculosClient, screenshot_equal, ApduResponse, ApduException

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

        self.apdu_logger.info("<= %s%4x", rapdu.data.hex(), rapdu.status)

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
                 log_apdu_file: Optional[Path] = None,
                 **kwargs):
        super().__init__(firmware=firmware, log_apdu_file=log_apdu_file)
        self._host = host
        self._port = port
        args = ["--model", firmware.device]
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
        self._screen_content: dict = {}

    @property
    def url(self) -> str:
        return f"http://{self._host}:{self._port}"

    def __enter__(self) -> "SpeculosBackend":
        self.logger.info(f"Starting {self.__class__.__name__} stream")
        self._client.__enter__()

        # Wait until some text is displayed on the screen.
        start = time()
        while not self._screen_content.get("events", []):
            # Give some time to other threads, and mostly Speculos one
            sleep(0.2)
            if (time() - start > 10.0):
                raise TimeoutError(
                    "Timeout waiting for screen content upon Ragger Speculos Instance start")
            self._screen_content = self._client.get_current_screen_content()

        return self

    def __exit__(self, *args, **kwargs):
        self._client.__exit__(*args, **kwargs)

    def send_raw(self, data: bytes = b"") -> None:
        self.apdu_logger.info("=> %s", data.hex())
        self._pending = ApduResponse(self._client._apdu_exchange_nowait(data))

    @raise_policy_enforcer
    def receive(self) -> RAPDU:
        assert self._pending is not None
        result = RAPDU(0x9000, self._pending.receive())
        return result

    @raise_policy_enforcer
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        self.apdu_logger.info("=> %s", data.hex())
        return RAPDU(0x9000, self._client._apdu_exchange(data))

    @raise_policy_enforcer
    def _get_last_async_response(self, response) -> RAPDU:
        return RAPDU(0x9000, response.receive())

    @contextmanager
    def exchange_async_raw(self, data: bytes = b"") -> Generator[None, None, None]:
        self.apdu_logger.info("=> %s", data.hex())
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

    def finger_touch(self, x: int = 0, y: int = 0, delay: float = 0.5) -> None:
        self._client.finger_touch(x, y, delay)

    def _save_screen_snapshot(self, snap: BytesIO, path: Path) -> None:
        self.logger.info(f"Saving screenshot to image '{path}'")
        img = Image.open(snap)
        img.save(path)

    def compare_screen_with_snapshot(self,
                                     golden_snap_path: Path,
                                     crop: Optional[Crop] = None,
                                     tmp_snap_path: Optional[Path] = None,
                                     golden_run: bool = False) -> bool:
        snap = BytesIO(self._client.get_screenshot())

        # Save snap in tmp folder.
        # It allows the user to access the screenshots in case of comparison failure
        if tmp_snap_path:
            self._save_screen_snapshot(snap, tmp_snap_path)

        # Allow to generate golden snapshots
        if golden_run:
            self._save_screen_snapshot(snap, golden_snap_path)

        if crop is not None:
            return screenshot_equal(f"{golden_snap_path}",
                                    snap,
                                    left=crop.left,
                                    upper=crop.upper,
                                    right=crop.right,
                                    lower=crop.lower)
        else:
            return screenshot_equal(f"{golden_snap_path}", snap)

    def get_current_screen_content(self) -> dict:
        self._screen_content = self._client.get_current_screen_content()
        return self._screen_content

    def compare_screen_with_text(self, text: str) -> bool:
        return text in dumps(self._client.get_current_screen_content())

    def wait_for_screen_change(self, timeout: float = 10.0) -> None:
        start = time()
        content = self._client.get_current_screen_content()
        while content == self._screen_content:
            # Give some time to other threads, and mostly Speculos one
            sleep(0.2)
            if (time() - start > timeout):
                raise TimeoutError("Timeout waiting for screen change")
            content = self._client.get_current_screen_content()

        # Speculos has received at least one new event to redisplay the screen
        # Wait a bit to ensure the event batch is received and processed by Speculos before returning
        sleep(0.2)

        # Update self._screen_content to use it as reference for next calls
        self._screen_content = self._client.get_current_screen_content()
        self.logger.info(f"Received new screen event '{self._screen_content}'")
