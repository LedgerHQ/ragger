import logging

logger = logging.getLogger(__package__)
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('[%(asctime)s][%(levelname)s] %(name)s - %(message)s'))

logger.addHandler(handler)
