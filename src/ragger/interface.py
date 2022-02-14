from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type

from ragger.utils import pack_APDU


@dataclass(frozen=True)
class RAPDU:
    status: int
    data: bytes


class BackendInterface(ABC):

    def __init__(self, host: str, port: int, raises: bool = False):
        """Initializes the Backend

        :param host: The host where to reach the backend.
        :type host: str
        :param port: The port where to reach the backend
        :type port: int
        :param raises: Weither the instance should raises on non-0x9000 response
                       statuses, or not.
        :type raises: bool
        """
        self._host = host
        self._port = port
        self._raises = raises

    @property
    def raises(self) -> bool:
        """
        :return: Weither the instance raises on non-0x9000 response statuses or not.
        :rtype: bool
        """
        return self._raises

    @property
    def url(self) -> str:
        """
        :return: The backend URL.
        :rtype: str
        """
        return f"{self._host}:{self._port}"

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

        :return: Nothing
        :rtype: None
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

        :return: Nothing
        :rtype: None
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
                               different from 0x9000

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
                               different from 0x9000

        :return: The APDU response
        :rtype: RAPDU
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

        :return: Nothing
        :rtype: None
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

        :return: Nothing
        :rtype: None
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

        :return: Nothing
        :rtype: None
        """
        raise NotImplementedError
