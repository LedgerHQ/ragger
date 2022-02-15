from pathlib import Path
from typing import Optional

from speculos.client import SpeculosClient, ApduResponse, ApduException

from ragger import logger
from ragger.interface import BackendInterface, RAPDU


def manage_error(function):

    def decoration(*args, **kwargs) -> RAPDU:
        self: SpeculosBackend = args[0]
        try:
            rapdu = function(*args, **kwargs)
        except ApduException as error:
            if self.raises:
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
                 **kwargs):
        super().__init__(host, port, raises=raises)
        self._client: SpeculosClient = SpeculosClient(app=str(application),
                                                      api_url=self.url,
                                                      **kwargs)
        self._pending: Optional[ApduResponse] = None

    @property
    def url(self) -> str:
        return f"http://{super().url}"

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

    def right_click(self) -> None:
        self._client.press_and_release("right")

    def left_click(self) -> None:
        self._client.press_and_release("left")

    def both_click(self) -> None:
        self._client.press_and_release("both")
