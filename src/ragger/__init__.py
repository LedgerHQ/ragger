import logging

logger = logging.getLogger(__package__)
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(name)s - %(message)s'))

logger.addHandler(handler)


from ragger.speculos import SpeculosBackend
from ragger.ledgercomm import LedgerCommBackend

__all__ = [SpeculosBackend, LedgerCommBackend]
