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
import logging

from ragger.backend import BackendInterface
from ragger.firmware import Firmware
from .positions import POSITIONS_BY_SDK


class Layout:

    def __init__(self, client: BackendInterface, firmware: Firmware):
        self._client = client
        assert firmware.semantic_version in POSITIONS_BY_SDK, \
            f"This firmware {firmware} is not compatible with layouts"
        self._firmware = firmware

    @property
    def client(self) -> BackendInterface:
        return self._client

    @property
    def firmware(self) -> Firmware:
        return self._firmware

    @property
    def positions(self):
        return POSITIONS_BY_SDK[self._firmware.semantic_version][str(self.__class__.__name__)]


# Center
########


# Suggestions
class ChoiceList(Layout):

    def choose(self, index: int):
        assert 1 <= index <= 6, "Choice index must be in [1, 6]"
        self.client.finger_touch(*self.positions[index])


class Suggestions(Layout):

    def choose(self, index: int):
        assert 1 <= index <= 4, "Suggestion index must be in [1, 4]"
        self.client.finger_touch(*self.positions[index])


# Keyboards
class LetterOnlyKeyboard(Layout):

    def write(self, word: str):
        for letter in word.lower():
            logging.info("Writting letter '%s', position '%s'", letter, self.positions[letter])
            self.client.finger_touch(*self.positions[letter])

    def back(self):
        self.client.finger_touch(*self.positions["back"])


# Center Info
class TappableCenter(Layout):

    def tap(self):
        self.client.finger_touch(*self.positions)


# Headers
#########
class InfoHeader(Layout):

    def tap(self):
        self.client.finger_touch(*self.positions)


class NavigationHeader(Layout):

    def tap(self):
        self.client.finger_touch(*self.positions)


# Footers
#########
class CancelFooter(Layout):

    def tap(self):
        self.client.finger_touch(*self.positions)
