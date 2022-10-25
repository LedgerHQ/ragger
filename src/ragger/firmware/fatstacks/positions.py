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
from dataclasses import astuple, dataclass

from ragger.firmware.versions import FatstacksVersions


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __iter__(self):
        return iter(astuple(self))


# Fatstacks resolution is 400x670
CENTER = Position(200, 335)
BUTTON_UPPER_LEFT = Position(36, 36)
BUTTON_UPPER_RIGHT = Position(342, 55)
BUTTON_LOWER_MIDDLE = Position(197, 606)

POSITIONS_BY_SDK = {
    FatstacksVersions.V_1_0_0.value: {
        "ChoiceList": {
            # Up to 6 (5?) choice in a list
            1: Position(200, 190),
            2: Position(200, 260),
            3: Position(200, 340),
            4: Position(200, 410),
            5: Position(200, 480),
            6: Position(200, 550)
        },
        "Suggestions": {
            # 4 suggestions max, 2 rows of 2
            # indexes for left to right, from up to down
            1: Position(100, 235),
            2: Position(290, 235),
            3: Position(110, 305),
            4: Position(290, 305),
        },
        "LetterOnlyKeyboard": {
            "q": Position(20, 470),
            "w": Position(60, 470),
            "e": Position(100, 470),
            "r": Position(140, 470),
            "t": Position(180, 470),
            "y": Position(220, 470),
            "u": Position(260, 470),
            "i": Position(300, 470),
            "o": Position(340, 470),
            "p": Position(380, 470),
            "a": Position(40, 525),
            "s": Position(80, 525),
            "d": Position(120, 525),
            "f": Position(160, 525),
            "g": Position(200, 525),
            "h": Position(240, 525),
            "j": Position(280, 525),
            "k": Position(320, 525),
            "l": Position(360, 525),
            "z": Position(20, 580),
            "x": Position(60, 580),
            "c": Position(100, 580),
            "v": Position(140, 580),
            "b": Position(180, 580),
            "n": Position(220, 580),
            "m": Position(260, 580),
            "back": Position(340, 580),
        },
        "TappableCenter": CENTER,
        "InfoHeader": BUTTON_UPPER_RIGHT,
        "NavigationHeader": BUTTON_UPPER_LEFT,
        "CancelFooter": BUTTON_LOWER_MIDDLE,
    }
}
