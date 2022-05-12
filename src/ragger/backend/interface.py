from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type, Iterable, Generator

from ragger.utils import pack_APDU


@dataclass(frozen=True)
class RAPDU:
    status: int
    data: bytes

    def __str__(self):
        return f'[0x{self.status:02x}] {self.data.hex() if self.data else "<Nothing>"}'


class BackendInterface(ABC):

    def __init__(self,
                 raises: bool = False,
                 valid_statuses: Iterable[int] = (0x9000, )):
        """Initializes the Backend

        :param raises: Weither the instance should raises on non-valid response
                       statuses, or not.
        :type raises: bool
        :param valid_statuses: a list of RAPDU statuses considered successfull
                               (default: [0x9000])
        :type valid_statuses: any iterable
        """
        self._raises = raises
        self._valid_statuses = valid_statuses
        self._last_async_response: Optional[RAPDU] = None

    @property
    def last_async_response(self) -> Optional[RAPDU]:
        """
        :return: The last RAPDU received after a call to `exchange_async` or
                 `exchange_async_raw`. `None` if no called was made, or if it
                 resulted into an exception throw.
        :rtype: RAPDU
        """
        return self._last_async_response

    @property
    def raises(self) -> bool:
        """
        :return: Weither the instance raises on non-0x9000 response statuses or
                 not.
        :rtype: bool
        """
        return self._raises

    def is_valid(self, status: int) -> bool:
        """
        :param status: A status to check
        :type status: int

        :return: If the given status is considered valid or not
        :rtype: bool
        """
        return status in self._valid_statuses

    @abstractmethod
    def __enter__(self) -> "BackendInterface":
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType]):
        raise NotImplementedError

    def send(self,
             cla: int,
             ins: int,
             p1: int = 0,
             p2: int = 0,
             data: bytes = b"") -> None:
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

        :raises ApduException: If the `raises` attribute is True, this method
                               will raise if the backend returns a status code
                               not registered a a `valid_statuses`

        :return: The APDU response
        :rtype: RAPDU
        """
        raise NotImplementedError

    def exchange(self,
                 cla: int,
                 ins: int,
                 p1: int = 0,
                 p2: int = 0,
                 data: bytes = b"") -> RAPDU:
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

        :raises ApduException: If the `raises` attribute is True, this method
                               will raise if the backend returns a status code
                               different from 0x9000

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

        :raises ApduException: If the `raises` attribute is True, this method
                               will raise if the backend returns a status code
                               not registered a a `valid_statuses`

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

        :raises ApduException: If the `raises` attribute is True, this method
                               will raise if the backend returns a status code
                               not registered a a `valid_statuses`

        :return: None
        :rtype: NoneType
        """
        with self.exchange_async_raw(pack_APDU(cla, ins, p1, p2, data)):
            yield

    @contextmanager
    @abstractmethod
    def exchange_async_raw(self,
                           data: bytes = b"") -> Generator[None, None, None]:
        """
        Sends the given APDU to the backend, then gives the control back to the
        caller.

        Every part of the APDU (including length) are the caller's
        responsibility

        :param data: The APDU message
        :type data: bytes

        :raises ApduException: If the `raises` attribute is True, this method
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
