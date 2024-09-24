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

from ragger.firmware import Firmware


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __iter__(self):
        return iter(astuple(self))


# Stax resolution is 400x670
STAX_CENTER = Position(200, 335)
# Flex resolution is 480x600
FLEX_CENTER = Position(240, 300)

STAX_BUTTON_UPPER_CENTER_MIDDLE = Position(200, 280)
FLEX_BUTTON_UPPER_CENTER_MIDDLE = Position(240, 250)

STAX_BUTTON_UPPER_LEFT = Position(36, 36)
FLEX_BUTTON_UPPER_LEFT = Position(45, 45)

STAX_BUTTON_UPPER_RIGHT = Position(342, 55)
FLEX_BUTTON_UPPER_RIGHT = Position(405, 75)

STAX_BUTTON_LOWER_LEFT = Position(36, 606)
FLEX_BUTTON_LOWER_LEFT = Position(55, 530)

STAX_BUTTON_LOWER_MIDDLE = Position(200, 606)
FLEX_BUTTON_LOWER_MIDDLE = Position(240, 550)

STAX_BUTTON_LOWER_RIGHT = Position(342, 606)
FLEX_BUTTON_LOWER_RIGHT = Position(430, 550)
STAX_BUTTON_LOWER_MIDDLE_RIGHT = Position(266, 615)
FLEX_BUTTON_LOWER_MIDDLE_RIGHT = Position(320, 550)

STAX_BUTTON_ABOVE_LOWER_MIDDLE = Position(200, 515)
FLEX_BUTTON_ABOVE_LOWER_MIDDLE = Position(240, 435)

POSITIONS = {
    "Center": {
        Firmware.STAX: STAX_CENTER,
        Firmware.FLEX: FLEX_CENTER,
    },
    "ChoiceList": {
        Firmware.STAX: {
            # Up to 5 choices in a list
            1: Position(200, 140),
            2: Position(200, 235),
            3: Position(200, 330),
            4: Position(200, 425),
            5: Position(200, 520),
        },
        Firmware.FLEX: {
            # Up to 5 choices in a list
            1: Position(240, 150),
            2: Position(240, 240),
            3: Position(240, 330),
            4: Position(240, 420),
            5: Position(240, 510),
        }
    },
    "Suggestions": {
        Firmware.STAX: {
            # 4 suggestions max, 2 rows of 2
            # indexes for left to right, from up to down
            1: Position(100, 280),
            2: Position(290, 280),
            3: Position(110, 350),
            4: Position(290, 350),
        },
        Firmware.FLEX: {
            # On Flex, suggestions are on a single line, which can be swiped to access the last
            # ones. At start, only 2 suggestions are clickable
            1: Position(140, 300),
            2: Position(350, 300),
        },
    },
    "LetterOnlyKeyboard": {
        Firmware.STAX: {
            # first line
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
            # second line
            "a": Position(40, 525),
            "s": Position(80, 525),
            "d": Position(120, 525),
            "f": Position(160, 525),
            "g": Position(200, 525),
            "h": Position(240, 525),
            "j": Position(280, 525),
            "k": Position(320, 525),
            "l": Position(360, 525),
            # third and last line
            "z": Position(20, 580),
            "x": Position(60, 580),
            "c": Position(100, 580),
            "v": Position(140, 580),
            "b": Position(180, 580),
            "n": Position(220, 580),
            "m": Position(260, 580),
            "back": Position(340, 580),
        },
        Firmware.FLEX: {
            # first line
            "q": Position(24, 415),
            "w": Position(72, 415),
            "e": Position(120, 415),
            "r": Position(168, 415),
            "t": Position(216, 415),
            "y": Position(264, 415),
            "u": Position(312, 415),
            "i": Position(360, 415),
            "o": Position(408, 415),
            "p": Position(456, 415),
            # second line
            "a": Position(48, 490),
            "s": Position(96, 490),
            "d": Position(144, 490),
            "f": Position(192, 490),
            "g": Position(240, 490),
            "h": Position(288, 490),
            "j": Position(336, 490),
            "k": Position(384, 490),
            "l": Position(432, 490),
            # third and last line
            "z": Position(24, 565),
            "x": Position(72, 565),
            "c": Position(120, 565),
            "v": Position(168, 565),
            "b": Position(216, 565),
            "n": Position(264, 565),
            "m": Position(312, 565),
            "back": Position(400, 565),
        }
    },
    "FullKeyboardLetters": {
        Firmware.STAX: {
            # first line
            "q": Position(20, 415),
            "w": Position(60, 415),
            "e": Position(100, 415),
            "r": Position(140, 415),
            "t": Position(180, 415),
            "y": Position(220, 415),
            "u": Position(260, 415),
            "i": Position(300, 415),
            "o": Position(340, 415),
            "p": Position(380, 415),
            # second line
            "a": Position(40, 470),
            "s": Position(80, 470),
            "d": Position(120, 470),
            "f": Position(160, 470),
            "g": Position(200, 470),
            "h": Position(240, 470),
            "j": Position(280, 470),
            "k": Position(320, 470),
            "l": Position(360, 470),
            # third line
            "z": Position(80, 525),
            "x": Position(120, 525),
            "c": Position(160, 525),
            "v": Position(200, 525),
            "b": Position(240, 525),
            "n": Position(280, 525),
            "m": Position(320, 525),
            "change_case": Position(30, 525),
            "back": Position(380, 525),
            # fourth and last line
            " ": Position(250, 580),
            "change_layout": Position(70, 580),
        },
        Firmware.FLEX: {
            # first line
            "q": Position(24, 350),
            "w": Position(72, 350),
            "e": Position(120, 350),
            "r": Position(168, 350),
            "t": Position(216, 350),
            "y": Position(264, 350),
            "u": Position(312, 350),
            "i": Position(360, 350),
            "o": Position(408, 350),
            "p": Position(456, 350),
            # second line
            "a": Position(48, 420),
            "s": Position(96, 420),
            "d": Position(144, 420),
            "f": Position(192, 420),
            "g": Position(240, 420),
            "h": Position(288, 420),
            "j": Position(336, 420),
            "k": Position(384, 420),
            "l": Position(432, 420),
            # third line
            "z": Position(96, 490),
            "x": Position(144, 490),
            "c": Position(192, 490),
            "v": Position(240, 490),
            "b": Position(288, 490),
            "n": Position(336, 490),
            "m": Position(384, 490),
            "change_case": Position(36, 490),
            "back": Position(444, 490),
            # fourth and last line
            "change_layout": Position(72, 560),
            " ": Position(312, 560),
        }
    },
    "FullKeyboardSpecialCharacters1": {
        Firmware.STAX: {
            # first line
            "1": Position(20, 415),
            "2": Position(60, 415),
            "3": Position(100, 415),
            "4": Position(140, 415),
            "5": Position(180, 415),
            "6": Position(220, 415),
            "7": Position(260, 415),
            "8": Position(300, 415),
            "9": Position(340, 415),
            "0": Position(380, 415),
            # second line
            "-": Position(40, 470),
            "/": Position(80, 470),
            ":": Position(120, 470),
            ";": Position(160, 470),
            "(": Position(200, 470),
            ")": Position(240, 470),
            "&": Position(280, 470),
            "@": Position(320, 470),
            "\"": Position(360, 470),
            # third line
            "more_specials": Position(50, 525),
            ".": Position(120, 525),
            ",": Position(160, 525),
            "?": Position(200, 525),
            "!": Position(240, 525),
            "'": Position(280, 525),
            "back": Position(380, 525),
            # fourth and last line
            "change_layout": Position(70, 580),
            " ": Position(250, 580),
        },
        Firmware.FLEX: {
            # first line
            "1": Position(24, 350),
            "2": Position(72, 350),
            "3": Position(120, 350),
            "4": Position(168, 350),
            "5": Position(216, 350),
            "6": Position(264, 350),
            "7": Position(312, 350),
            "8": Position(360, 350),
            "9": Position(408, 350),
            "0": Position(456, 350),
            # second line
            "-": Position(48, 420),
            "/": Position(96, 420),
            ":": Position(144, 420),
            ";": Position(192, 420),
            "(": Position(240, 420),
            ")": Position(288, 420),
            "&": Position(336, 420),
            "@": Position(384, 420),
            "\"": Position(432, 420),
            # third line
            "more_specials": Position(60, 490),
            ".": Position(144, 490),
            ",": Position(192, 490),
            "?": Position(240, 490),
            "!": Position(288, 490),
            "'": Position(336, 490),
            "back": Position(420, 490),
            # fourth and last line
            "change_layout": Position(72, 560),
            " ": Position(312, 560),
        }
    },
    "FullKeyboardSpecialCharacters2": {
        Firmware.STAX: {
            # first line
            "[": Position(20, 415),
            "]": Position(60, 415),
            "{": Position(100, 415),
            "}": Position(140, 415),
            "#": Position(180, 415),
            "%": Position(220, 415),
            "^": Position(260, 415),
            "*": Position(300, 415),
            "+": Position(340, 415),
            "=": Position(380, 415),
            # second line
            "_": Position(40, 470),
            "\\": Position(80, 470),
            "|": Position(120, 470),
            "~": Position(160, 470),
            "<": Position(200, 470),
            ">": Position(240, 470),
            "$": Position(280, 470),
            "`": Position(320, 470),
            "\"": Position(360, 470),
            # third line
            "more_specials": Position(50, 525),
            ".": Position(120, 525),
            ",": Position(160, 525),
            "?": Position(200, 525),
            "!": Position(240, 525),
            "'": Position(280, 525),
            "back": Position(380, 525),
            # fourth and last line
            "change_layout": Position(70, 580),
            " ": Position(250, 580),
        },
        Firmware.FLEX: {
            # first line
            "[": Position(24, 350),
            "]": Position(72, 350),
            "{": Position(120, 350),
            "}": Position(168, 350),
            "#": Position(216, 350),
            "%": Position(264, 350),
            "^": Position(312, 350),
            "*": Position(360, 350),
            "+": Position(408, 350),
            "=": Position(456, 350),
            # second line
            "_": Position(48, 420),
            "\\": Position(96, 420),
            "|": Position(144, 420),
            "~": Position(192, 420),
            ">": Position(240, 420),
            "<": Position(288, 420),
            "$": Position(336, 420),
            "`": Position(384, 420),
            "\"": Position(432, 420),
            # third line
            "more_specials": Position(60, 490),
            ".": Position(144, 490),
            ",": Position(192, 490),
            "?": Position(240, 490),
            "!": Position(288, 490),
            "'": Position(336, 490),
            "back": Position(420, 490),
            # fourth and last line
            "change_layout": Position(72, 560),
            " ": Position(312, 560),
        }
    },
    "TappableCenter": {
        Firmware.STAX: STAX_CENTER,
        Firmware.FLEX: FLEX_CENTER,
    },
    "KeyboardConfirmationButton": {
        Firmware.STAX: STAX_BUTTON_UPPER_CENTER_MIDDLE,
        Firmware.FLEX: FLEX_BUTTON_UPPER_CENTER_MIDDLE,
    },
    "RightHeader": {
        Firmware.STAX: STAX_BUTTON_UPPER_RIGHT,
        Firmware.FLEX: FLEX_BUTTON_UPPER_RIGHT
    },
    "LeftHeader": {
        Firmware.STAX: STAX_BUTTON_UPPER_LEFT,
        Firmware.FLEX: FLEX_BUTTON_UPPER_LEFT
    },
    "CenteredFooter": {
        Firmware.STAX: STAX_BUTTON_LOWER_MIDDLE,
        Firmware.FLEX: FLEX_BUTTON_LOWER_MIDDLE
    },
    "LeftFooter": {
        Firmware.STAX: STAX_BUTTON_LOWER_LEFT,
        Firmware.FLEX: FLEX_BUTTON_LOWER_LEFT
    },
    "CancelFooter": {
        Firmware.STAX: STAX_BUTTON_LOWER_LEFT,
        Firmware.FLEX: FLEX_BUTTON_LOWER_LEFT
    },
    "UseCaseHome": {
        Firmware.STAX: {
            "info": STAX_BUTTON_UPPER_RIGHT,
            "settings": STAX_BUTTON_UPPER_RIGHT,
            "quit": STAX_BUTTON_LOWER_MIDDLE
        },
        Firmware.FLEX: {
            "info": FLEX_BUTTON_UPPER_RIGHT,
            "settings": FLEX_BUTTON_UPPER_RIGHT,
            "quit": FLEX_BUTTON_LOWER_MIDDLE
        }
    },
    "UseCaseHomeExt": {
        Firmware.STAX: {
            "info": STAX_BUTTON_UPPER_RIGHT,
            "settings": STAX_BUTTON_UPPER_RIGHT,
            "action": STAX_BUTTON_ABOVE_LOWER_MIDDLE,
            "quit": STAX_BUTTON_LOWER_MIDDLE
        },
        Firmware.FLEX: {
            "info": FLEX_BUTTON_UPPER_RIGHT,
            "settings": FLEX_BUTTON_UPPER_RIGHT,
            "action": FLEX_BUTTON_ABOVE_LOWER_MIDDLE,
            "quit": FLEX_BUTTON_LOWER_MIDDLE
        }
    },
    "UseCaseSettings": {
        Firmware.STAX: {
            "single_page_exit": STAX_BUTTON_UPPER_LEFT,
            "multi_page_exit": STAX_BUTTON_UPPER_LEFT,
            "previous": STAX_BUTTON_LOWER_MIDDLE_RIGHT,
            "next": STAX_BUTTON_LOWER_RIGHT,
        },
        Firmware.FLEX: {
            "single_page_exit": FLEX_BUTTON_UPPER_LEFT,
            "multi_page_exit": FLEX_BUTTON_UPPER_LEFT,
            "previous": FLEX_BUTTON_LOWER_MIDDLE_RIGHT,
            "next": FLEX_BUTTON_LOWER_RIGHT,
        }
    },
    "UseCaseSubSettings": {
        Firmware.STAX: {
            "exit": STAX_BUTTON_UPPER_LEFT,
            "previous": STAX_BUTTON_LOWER_LEFT,
            "next": STAX_BUTTON_LOWER_RIGHT,
        },
        Firmware.FLEX: {
            "exit": FLEX_BUTTON_UPPER_LEFT,
            "previous": FLEX_BUTTON_LOWER_LEFT,
            "next": FLEX_BUTTON_LOWER_RIGHT,
        }
    },
    "UseCaseChoice": {
        Firmware.STAX: {
            "confirm": STAX_BUTTON_ABOVE_LOWER_MIDDLE,
            "reject": STAX_BUTTON_LOWER_LEFT,
        },
        Firmware.FLEX: {
            "confirm": FLEX_BUTTON_ABOVE_LOWER_MIDDLE,
            "reject": FLEX_BUTTON_LOWER_LEFT,
        }
    },
    "UseCaseStatus": {
        Firmware.STAX: {
            "dismiss": STAX_CENTER,
        },
        Firmware.FLEX: {
            "dismiss": FLEX_CENTER,
        }
    },
    "UseCaseReview": {
        Firmware.STAX: {
            "tap": STAX_BUTTON_LOWER_RIGHT,
            "previous": STAX_BUTTON_LOWER_MIDDLE,
            "confirm": STAX_BUTTON_ABOVE_LOWER_MIDDLE,
            "reject": STAX_BUTTON_LOWER_LEFT,
        },
        Firmware.FLEX: {
            "tap": FLEX_BUTTON_LOWER_RIGHT,
            "previous": FLEX_BUTTON_LOWER_MIDDLE,
            "confirm": FLEX_BUTTON_ABOVE_LOWER_MIDDLE,
            "reject": FLEX_BUTTON_LOWER_LEFT,
        }
    },
    "UseCaseViewDetails": {
        Firmware.STAX: {
            "exit": STAX_BUTTON_LOWER_LEFT,
            "previous": STAX_BUTTON_LOWER_MIDDLE,
            "next": STAX_BUTTON_LOWER_RIGHT,
        },
        Firmware.FLEX: {
            "exit": FLEX_BUTTON_LOWER_LEFT,
            "previous": FLEX_BUTTON_LOWER_MIDDLE,
            "next": FLEX_BUTTON_LOWER_RIGHT,
        }
    },
    "UseCaseAddressConfirmation": {
        Firmware.STAX: {
            "tap": STAX_BUTTON_ABOVE_LOWER_MIDDLE,
            "exit_qr": STAX_BUTTON_LOWER_MIDDLE,
            "confirm": STAX_BUTTON_ABOVE_LOWER_MIDDLE,
            "cancel": STAX_BUTTON_LOWER_LEFT,
        },
        Firmware.FLEX: {
            "tap": FLEX_BUTTON_ABOVE_LOWER_MIDDLE,
            "exit_qr": FLEX_BUTTON_LOWER_MIDDLE,
            "confirm": FLEX_BUTTON_ABOVE_LOWER_MIDDLE,
            "cancel": FLEX_BUTTON_LOWER_LEFT,
        }
    },
}
