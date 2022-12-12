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
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum, auto
from pathlib import Path
from types import TracebackType
from typing import Optional, Type, Generator

from ragger.firmware import Firmware
from ragger.utils import pack_APDU, RAPDU, Crop


class RaisePolicy(Enum):
    RAISE_NOTHING = auto()
    RAISE_ALL_BUT_0x9000 = auto()
    RAISE_ALL = auto()


class BackendInterface(ABC):

    def __init__(self, firmware: Firmware):
        """Initializes the Backend

        :param firmware: Which Firmware will be managed
        :type firmware: Firmware
        """
        self._firmware = firmware
        self._last_async_response: Optional[RAPDU] = None
        self.raise_policy = RaisePolicy.RAISE_ALL_BUT_0x9000

    @property
    def firmware(self) -> Firmware:
        """
        :return: The currently managed Firmware.
        :rtype: Firmware
        """
        return self._firmware

    @property
    def last_async_response(self) -> Optional[RAPDU]:
        """
        :return: The last RAPDU received after a call to `exchange_async` or
                 `exchange_async_raw`. `None` if no called was made, or if it
                 resulted into an exception throw.
        :rtype: RAPDU
        """
        return self._last_async_response

    @abstractmethod
    def __enter__(self) -> "BackendInterface":
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]):
        raise NotImplementedError

    def is_raise_required(self, rapdu: RAPDU) -> bool:
        """
        :return: If the given status is considered valid or not
        :rtype: bool
        """
        return ((self.raise_policy == RaisePolicy.RAISE_ALL)
                or ((self.raise_policy == RaisePolicy.RAISE_ALL_BUT_0x9000) and
                    (rapdu.status != 0x9000)))

    def send(self, cla: int, ins: int, p1: int = 0, p2: int = 0, data: bytes = b"") -> None:
        """
        Formats then sends an APDU to the backend.

        :param cla: The application ID
        :type cla: int
        :param ins: The command ID
        :type ins: int
        :param p1: First instruction parameter, defaults to 0
        :type p1: int
        :param p1: Second instruction parameter, defaults to 0
        :type p1: int
        :param data: Command data
        :type data: bytes

        :return: None
        :rtype: NoneType
        """
        return self.send_raw(pack_APDU(cla, ins, p1, p2, data))

    @abstractmethod
    def send_raw(self, data: bytes = b"") -> None:
        """
        Sends the given APDU to the backend.

        Every part of the APDU (including length) are the caller's
        responsibility

        :param data: The APDU message
        :type data: bytes

        :return: None
        :rtype: NoneType
        """
        raise NotImplementedError

    @abstractmethod
    def receive(self) -> RAPDU:
        """
        Receives a response APDU from the backend.

        Calling this method implies a command APDU has been previously sent
        to the backend, and a response is expected.

        :raises ExceptionRAPDU: If the `raises` attribute is True, this method
                                  will raise if the backend returns a status code
                                  not registered as a `valid_statuses`

        :return: The APDU response
        :rtype: RAPDU
        """
        raise NotImplementedError

    def exchange(self, cla: int, ins: int, p1: int = 0, p2: int = 0, data: bytes = b"") -> RAPDU:
        """
        Formats and sends an APDU to the backend, then receives its response.

        The length is automaticaly added to the APDU message.

        :param cla: The application ID
        :type cla: int
        :param ins: The command ID
        :type ins: int
        :param p1: First instruction parameter, defaults to 0
        :type p1: int
        :param p1: Second instruction parameter, defaults to 0
        :type p1: int
        :param data: Command data
        :type data: bytes

        :raises ExceptionRAPDU: If the `raises` attribute is True, this method
                                  will raise if the backend returns a status code
                                  not registered as a `valid_statuses`

        :return: The APDU response
        :rtype: RAPDU
        """
        return self.exchange_raw(pack_APDU(cla, ins, p1, p2, data))

    @abstractmethod
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        """
        Sends the given APDU to the backend, then receives its response.

        Every part of the APDU (including length) are the caller's
        responsibility

        :param data: The APDU message
        :type data: bytes

        :raises ExceptionRAPDU: If the `raises` attribute is True, this method
                                  will raise if the backend returns a status code
                                  not registered as a `valid_statuses`

        :return: The APDU response
        :rtype: RAPDU
        """
        raise NotImplementedError

    @contextmanager
    def exchange_async(self,
                       cla: int,
                       ins: int,
                       p1: int = 0,
                       p2: int = 0,
                       data: bytes = b"") -> Generator[None, None, None]:
        """
        Formats and sends an APDU to the backend, then gives the control back to
        the caller.

        This can be useful to still control a device when it has not responded
        yet, for instance when a UI validation is requested.

        The context manager does not yield anything. Interaction through the
        backend instance is still possible.

        :param cla: The application ID
        :type cla: int
        :param ins: The command ID
        :type ins: int
        :param p1: First instruction parameter, defaults to 0
        :type p1: int
        :param p1: Second instruction parameter, defaults to 0
        :type p1: int
        :param data: Command data
        :type data: bytes

        :raises ExceptionRAPDU: If the `raises` attribute is True, this method
                                  will raise if the backend returns a status code
                                  not registered as a `valid_statuses`

        :return: None
        :rtype: NoneType
        """
        with self.exchange_async_raw(pack_APDU(cla, ins, p1, p2, data)):
            yield

    @contextmanager
    @abstractmethod
    def exchange_async_raw(self, data: bytes = b"") -> Generator[None, None, None]:
        """
        Sends the given APDU to the backend, then gives the control back to the
        caller.

        Every part of the APDU (including length) are the caller's
        responsibility

        :param data: The APDU message
        :type data: bytes

        :raises ExceptionRAPDU: If the `raises` attribute is True, this method
                                  will raise if the backend returns a status code
                                  not registered a a `valid_statuses`

        :return: None
        :rtype: NoneType
        """
        raise NotImplementedError

    @abstractmethod
    def right_click(self) -> None:
        """
        Performs a right click on the device.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :return: None
        :rtype: NoneType
        """
        raise NotImplementedError

    @abstractmethod
    def left_click(self) -> None:
        """
        Performs a left click on the device.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :return: None
        :rtype: NoneType
        """
        raise NotImplementedError

    @abstractmethod
    def both_click(self) -> None:
        """
        Performs a click on both buttons of the device.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :return: None
        :rtype: NoneType
        """
        raise NotImplementedError

    @abstractmethod
    def finger_touch(self, x: int = 0, y: int = 0, delay: float = 0.5) -> None:
        """
        Performs a finger touch on the device screen.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :param x: The x coordinate of the finger touch.
        :type x: int
        :param y: The y coordinate of the finger touch.
        :type y: int
        :param delay: Delay between finger touch press and release actions.
        :type delay: float

        :return: None
        :rtype: NoneType
        """
        raise NotImplementedError

    @abstractmethod
    def compare_screen_with_snapshot(self,
                                     golden_snap_path: Path,
                                     crop: Optional[Crop] = None,
                                     tmp_snap_path: Optional[Path] = None,
                                     golden_run: bool = False) -> bool:
        """
        Compare the current device screen with the provided snapshot.

        :param golden_snap_path: The path to the snap to compare the screen
                                 device with
        :type golden_snap_path: Path
        :param crop: Optional crop options to use for the comparison
        :type crop: Crop
        :param tmp_snap_path: Optional path where to store the screen snap used
                              for the comparison
        :type tmp_snap_path: Path
        :param golden_run: Optional option to save the current screen as golden
                           instead of comparing it.
        :type golden_run: bool

        :return: True if matches else False
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def wait_for_screen_change(self, timeout: float = 10.0, context: list = []):
        """
        Wait until the screen content (text) changes compared to what is provided
        by the context parameter. If no context is provided, the function returns
        immediately, returning the current screen content.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :param timeout: Maximum time to wait for a screen change before an
                        exception is raised.
        :type timeout: float
        :param context: Context to compare screen content with.
        :type context: list
        :return: Latest screen content after the screen change.
        :rtype: list
        """
        raise NotImplementedError

    @abstractmethod
    def compare_screen_with_text(self, text: str):
        """
        Checks if the current screen content contains the text
        string provided.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :param text:
        :type text: str
        :return: True if the content contains the string, False
                 otherwise.
        :rtype: bool
        """
        raise NotImplementedError

    @abstractmethod
    def get_screen_content(self) -> list:
        """
        Returns the current screen content as a list.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :return: Current screen content as a list.
        :rtype: list
        """
        raise NotImplementedError
