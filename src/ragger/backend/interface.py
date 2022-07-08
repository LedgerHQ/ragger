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
from types import TracebackType
from typing import Optional, Type, Iterable, Generator
from enum import Enum, auto

from ragger.utils import pack_APDU, RAPDU, Firmware
from ragger.error import ExceptionRAPDU


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
