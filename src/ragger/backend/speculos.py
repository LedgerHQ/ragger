from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Iterable, Generator

from speculos.client import SpeculosClient, ApduResponse, ApduException

from ragger import logger
from .interface import BackendInterface, RAPDU


def manage_error(function):

    def decoration(self: 'SpeculosBackend', *args, **kwargs) -> RAPDU:
        try:
            rapdu = function(self, *args, **kwargs)
        except ApduException as error:
            if self.raises and not self.is_valid(error.sw):
                raise error
            rapdu = RAPDU(error.sw, error.data)
        logger.debug("Receiving '%s'", rapdu)
        return rapdu

    return decoration


class SpeculosBackend(BackendInterface):

    def __init__(self,
                 application: Path,
                 host: str = "127.0.0.1",
                 port: int = 5000,
                 raises: bool = False,
                 valid_statuses: Iterable[int] = (0x9000, ),
                 **kwargs):
        super().__init__(raises=raises, valid_statuses=valid_statuses)
        self._host = host
        self._port = port
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
        logger.debug("Sending '%s'", data)
        self._pending = ApduResponse(self._client._apdu_exchange_nowait(data))

    @manage_error
    def receive(self) -> RAPDU:
        assert self._pending is not None
        result = RAPDU(0x9000, self._pending.receive())
        logger.debug("Receiving '%s'", result)
        return result

    @manage_error
    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        logger.debug("Sending '%s'", data)
        return RAPDU(0x9000, self._client._apdu_exchange(data))

    @contextmanager
    def exchange_async_raw(self,
                           data: bytes = b"") -> Generator[None, None, None]:
        with self._client.apdu_exchange_nowait(cla=data[0],
                                               ins=data[1],
                                               p1=data[2],
                                               p2=data[3],
                                               data=data[5:]) as response:
            yield
            try:
                self._last_async_response = response.receive()
            except ApduException as error:
                if self.raises and not self.is_valid(error.sw):
                    raise error
                self._last_async_response = RAPDU(error.sw, error.data)

    def right_click(self) -> None:
        self._client.press_and_release("right")

    def left_click(self) -> None:
        self._client.press_and_release("left")

    def both_click(self) -> None:
        self._client.press_and_release("both")
