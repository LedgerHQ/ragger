from pathlib import Path
from typing import Optional, Tuple

from speculos.client import SpeculosClient, ApduResponse, ApduException

from ragger import logger
from ragger.interface import BackendInterface, APDUResponse


def manage_error(function):
    def decoration(*args, **kwargs) -> APDUResponse:
        self = args[0]
        if self.raises:
            return function(*args, **kwargs)
        # else status code are returned with data as a tuple
        try:
            result = (0x9000, function(*args, **kwargs))
        except ApduException as error:
            result = (error.sw, error.data)
        logger.debug("Receiving '[%d] %s'", result[0], result[1])
        return result
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

    def send_raw(self, data: bytes = "") -> None:
        logger.debug("Sending '%s'", data)
        self._pending = ApduResponse(self._client._apdu_exchange_nowait(data))

    @manage_error
    def receive(self) -> APDUResponse:
        result = self._pending.receive()
        logger.debug("Receiving '%s'", result)
        return result

    @manage_error
    def exchange_raw(self, data: bytes = "") -> APDUResponse:
        logger.debug("Sending '%s'", data)
        result = self._client._apdu_exchange(data)
        return result

    def right_click(self) -> None:
        self._client.press_and_release("right")

    def left_click(self) -> None:
        self._client.press_and_release("left")

    def both_click(self) -> None:
        self._client.press_and_release("both")
