import logging

from speculos.client import ApduException

logger = logging.getLogger(__package__)
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('[%(asctime)s][%(levelname)s] %(name)s - %(message)s'))

logger.addHandler(handler)

from ragger.speculos import SpeculosBackend  # noqa: E402
from ragger.ledgercomm import LedgerCommBackend  # noqa: E402

__all__ = ["SpeculosBackend", "LedgerCommBackend", "ApduException"]
