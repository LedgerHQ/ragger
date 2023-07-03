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


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __iter__(self):
        return iter(astuple(self))


# Stax resolution is 400x670
CENTER = Position(200, 335)
BUTTON_UPPER_LEFT = Position(36, 36)
BUTTON_UPPER_RIGHT = Position(342, 55)
BUTTON_LOWER_LEFT = Position(36, 606)
BUTTON_LOWER_MIDDLE = Position(200, 606)
BUTTON_LOWER_RIGHT = Position(342, 606)
BUTTON_ABOVE_LOWER_MIDDLE = Position(200, 515)

POSITIONS = {
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
        1: Position(100, 310),
        2: Position(290, 310),
        3: Position(110, 380),
        4: Position(290, 380),
    },
    "LetterOnlyKeyboard": {
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
    "FullKeyboardLetters": {
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
    "FullKeyboardSpecialCharacters1": {
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
        " ": Position(250, 580),
        "change_layout": Position(70, 580),
    },
    "FullKeyboardSpecialCharacters2": {
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
        " ": Position(250, 580),
        "change_layout": Position(70, 580),
    },
    "TappableCenter": CENTER,
    "RightHeader": BUTTON_UPPER_RIGHT,
    "LeftHeader": BUTTON_UPPER_LEFT,
    "CenteredFooter": BUTTON_LOWER_MIDDLE,
    "UseCaseHome": {
        "info": BUTTON_UPPER_RIGHT,
        "settings": BUTTON_UPPER_RIGHT,
        "quit": BUTTON_LOWER_MIDDLE
    },
    "UseCaseHomeExt": {
        "info": BUTTON_UPPER_RIGHT,
        "settings": BUTTON_UPPER_RIGHT,
        "action": BUTTON_ABOVE_LOWER_MIDDLE,
        "quit": BUTTON_LOWER_MIDDLE
    },
    "UseCaseSettings": {
        "single_page_exit": BUTTON_LOWER_MIDDLE,
        "multi_page_exit": BUTTON_LOWER_LEFT,
        "previous": BUTTON_LOWER_MIDDLE,
        "next": BUTTON_LOWER_RIGHT,
    },
    "UseCaseSubSettings": {
        "exit": BUTTON_UPPER_LEFT,
        "previous": BUTTON_LOWER_LEFT,
        "next": BUTTON_LOWER_RIGHT,
    },
    "UseCaseChoice": {
        "confirm": BUTTON_ABOVE_LOWER_MIDDLE,
        "reject": BUTTON_LOWER_MIDDLE,
    },
    "UseCaseStatus": {
        "dismiss": CENTER,
    },
    "UseCaseReview": {
        "tap": CENTER,
        "previous": BUTTON_UPPER_LEFT,
        "confirm": BUTTON_ABOVE_LOWER_MIDDLE,
        "reject": BUTTON_LOWER_MIDDLE,
    },
    "UseCaseViewDetails": {
        "exit": BUTTON_LOWER_LEFT,
        "previous": BUTTON_LOWER_MIDDLE,
        "next": BUTTON_LOWER_RIGHT,
    },
    "UseCaseAddressConfirmation": {
        "tap": BUTTON_ABOVE_LOWER_MIDDLE,
        "exit_qr": BUTTON_LOWER_MIDDLE,
        "confirm": BUTTON_ABOVE_LOWER_MIDDLE,
        "cancel": BUTTON_LOWER_MIDDLE,
    },
}
