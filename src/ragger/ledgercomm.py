from typing import Optional, Tuple

from ledgercomm import Transport
from speculos.client import ApduException

from ragger import logger
from ragger.interface import BackendInterface, APDUResponse


def manage_error(function):

    def decoration(*args, **kwargs) -> Optional[Tuple[int, bytes]]:
        self = args[0]
        status, data = function(*args, **kwargs)
        logger.debug("Receiving '[%d] %s'", status, data)
        if not self.raises:
            return (status, data)
        if status == 0x9000:
            return data
        # else should raise
        raise ApduException(status, data)

    return decoration


class LedgerCommBackend(BackendInterface):

    def __init__(self,
                 host: str = "127.0.0.1",
                 port: int = 9999,
                 raises: bool = False,
                 *args,
                 **kwargs):
        super().__init__(host, port, raises=raises)
        self._client: Optional[Transport] = None
        self._args = (args, kwargs)

    def __enter__(self) -> "LedgerCommBackend":
        logger.info(f"Starting {self.__class__.__name__} stream")
        self._client = Transport(server=self._host,
                                 port=self._port,
                                 *self._args[0],
                                 **self._args[1])
        return self

    def __exit__(self, *args, **kwargs):
        assert self._client is not None
        self._client.close()

    def send_raw(self, data: bytes = b"") -> None:
        logger.debug("Sending '%s'", data)
        assert self._client is not None
        self._client.send_raw(data)

    @manage_error
    def receive(self) -> APDUResponse:
        assert self._client is not None
        result = self._client.recv()
        logger.debug("Receiving '%s'", result)
        return result

    @manage_error
    def exchange_raw(self, data: bytes = b"") -> APDUResponse:
        logger.debug("Exchange: sending   > '%s'", data)
        assert self._client is not None
        result = self._client.exchange_raw(data)
        logger.debug("Exchange: receiving < '%s'", result)
        return result

    def right_click(self) -> None:
        pass

    def left_click(self) -> None:
        pass

    def both_click(self) -> None:
        pass
