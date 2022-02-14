from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type, Tuple

from ragger.utils import pack_APDU


@dataclass(frozen=True)
class RAPDU:
    status: int
    data: bytes


class BackendInterface(ABC):

    def __init__(self, host: str, port: int, raises: bool = False):
        self._host = host
        self._port = port
        self._raises = raises

    @property
    def raises(self):
        return self._raises

    @property
    def url(self) -> str:
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
        return self.send_raw(pack_APDU(cla, ins, p1, p2, data))

    @abstractmethod
    def send_raw(self, data: bytes = b"") -> None:
        raise NotImplementedError

    @abstractmethod
    def receive(self) -> RAPDU:
        raise NotImplementedError

    def exchange(self,
                 cla: int,
                 ins: int,
                 p1: int = 0,
                 p2: int = 0,
                 data: bytes = b"") -> RAPDU:
        return self.exchange_raw(pack_APDU(cla, ins, p1, p2, data))

    @abstractmethod
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        raise NotImplementedError

    @abstractmethod
    def right_click(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def left_click(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def both_click(self) -> None:
        raise NotImplementedError
