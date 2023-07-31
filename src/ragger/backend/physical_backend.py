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
from pathlib import Path
from PIL import Image, ImageOps
from types import TracebackType
from typing import List, Optional, Type

from ragger.firmware import Firmware
from ragger.gui import RaggerGUI
from ragger.navigator.instruction import NavInsID
from ragger.utils import Crop
from .interface import BackendInterface

try:
    from pytesseract import image_to_data, Output

    TESSERACT_AVAILABLE = True
except ImportError as e:
    if "pytesseract" not in str(e):
        raise e

    TESSERACT_AVAILABLE = False


class PhysicalBackend(BackendInterface):

    def __init__(self, firmware: Firmware, *args, with_gui: bool = False, **kwargs):
        super().__init__(firmware, *args, **kwargs)
        self._ui: Optional[RaggerGUI] = RaggerGUI(device=firmware.name) if with_gui else None
        self._last_valid_snap_path: Optional[Path] = None

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]] = None,
                 exc_val: Optional[BaseException] = None,
                 exc_tb: Optional[TracebackType] = None):
        if self._ui is not None:
            self._ui.kill()

    def init_gui(self) -> None:
        """
        Initialize the GUI if needed.
        """
        assert self._ui is not None, \
            "This method should only be called if the backend manages an GUI"
        if not self._ui.is_alive():
            self._ui.start()

    def right_click(self) -> None:
        if self._ui is None:
            return
        self.init_gui()
        self._ui.ask_for_click_action(NavInsID.RIGHT_CLICK)

    def left_click(self) -> None:
        if self._ui is None:
            return
        self.init_gui()
        self._ui.ask_for_click_action(NavInsID.LEFT_CLICK)

    def both_click(self) -> None:
        if self._ui is None:
            return
        self.init_gui()
        self._ui.ask_for_click_action(NavInsID.BOTH_CLICK)

    def finger_touch(self, x: int = 0, y: int = 0, delay: float = 0.5) -> None:
        if self._ui is None:
            return
        self.init_gui()
        self._ui.ask_for_touch_action(x, y)

    def compare_screen_with_snapshot(self,
                                     golden_snap_path: Path,
                                     crop: Optional[Crop] = None,
                                     tmp_snap_path: Optional[Path] = None,
                                     golden_run: bool = False) -> bool:
        if self._ui is None:
            return True
        self.init_gui()

        # If for some reason we ask to compare the same snapshot twice, just return True.
        if self._last_valid_snap_path == golden_snap_path:
            return True

        if self._ui.check_screenshot(golden_snap_path):
            self._last_valid_snap_path = golden_snap_path
            return True
        else:
            self._last_valid_snap_path = None
            return False

    def compare_screen_with_text(self, text: str) -> bool:
        if self._ui is None:
            return True
        self.init_gui()
        if self._last_valid_snap_path:
            if not TESSERACT_AVAILABLE:
                raise ImportError("Missing pytesseract module for this usage")
            image = Image.open(self._last_valid_snap_path)
            # Nano (s,sp,x) snapshots are white/blue text on black background,
            # tesseract cannot do OCR on these. Invert image so it has
            # dark text on white background.
            if self.firmware.is_nano:
                image = ImageOps.invert(image)
            data = image_to_data(image, output_type=Output.DICT)
            for item in range(len(data["text"])):
                if text in data["text"][item]:
                    return True
            return False
        else:
            return self._ui.check_text(text)

    def wait_for_screen_change(self, timeout: float = 10.0) -> None:
        return

    def get_current_screen_content(self) -> List:
        return list()

    def pause_ticker(self) -> None:
        pass

    def resume_ticker(self) -> None:
        pass

    def send_tick(self) -> None:
        pass
