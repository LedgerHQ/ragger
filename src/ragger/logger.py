"""
   Copyright 2022 Ledger SAS

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import atexit
import logging
from pathlib import Path
from typing import Optional

DEFAULT_FORMAT = '[%(asctime)s][%(levelname)s] %(name)s - %(message)s'


def get_default_logger():
    return logging.getLogger("ragger.logger")


def get_apdu_logger():
    return logging.getLogger("ragger.apdu_logger")


def get_gui_logger():
    return logging.getLogger("ragger.gui")


def _init_logger(logger: logging.Logger, format: Optional[str]):
    format = format or DEFAULT_FORMAT
    logger.handlers.clear()
    logger.setLevel(level=logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)


def init_loggers(format: Optional[str] = None):
    for logger in [get_default_logger(), get_apdu_logger(), get_gui_logger()]:
        _init_logger(logger, format)


def set_apdu_logger_file(log_apdu_file: Path):
    apdu_logger = get_apdu_logger()

    # Only one file handler supported
    for handler in apdu_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            apdu_logger.removeHandler(handler)

    apdu_handler = logging.FileHandler(filename=log_apdu_file, mode='w', delay=True)
    apdu_handler.setFormatter(logging.Formatter('%(message)s'))
    apdu_logger.addHandler(apdu_handler)

    def cleanup():
        for handler in apdu_logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()

    atexit.register(cleanup)
