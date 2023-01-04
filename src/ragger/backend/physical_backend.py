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
from typing import Any, Optional

from ragger.gui import RaggerGUI
from ragger.navigator import NavInsID
from ragger.utils import Crop
from .interface import BackendInterface


class PhysicalBackend(BackendInterface):

    def __init__(self, *args, with_gui: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self._ui: Optional[RaggerGUI] = RaggerGUI() if with_gui else None

    def init_gui(self):
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
        self._ui.ask_for_action(NavInsID.RIGHT_CLICK)

    def left_click(self) -> None:
        if self._ui is None:
            return
        self.init_gui()
        self._ui.ask_for_action(NavInsID.LEFT_CLICK)

    def both_click(self) -> None:
        if self._ui is None:
            return
        self.init_gui()
        self._ui.ask_for_action(NavInsID.BOTH_CLICK)

    def compare_screen_with_snapshot(self,
                                     golden_snap_path: Path,
                                     crop: Optional[Crop] = None,
                                     tmp_snap_path: Optional[Path] = None,
                                     golden_run: bool = False) -> bool:
        if self._ui is None:
            return True
        self.init_gui()
        return self._ui.check_screenshot(golden_snap_path)

    def finger_touch(self, x: int = 0, y: int = 0, delay: float = 0.5) -> None:
        pass

    def wait_for_screen_change(self, timeout: float = 10.0) -> None:
        return

    def compare_screen_with_text(self, text: str) -> bool:
        return True

    def get_current_screen_content(self) -> Any:
        return []

    def __del__(self):
        if self._ui is not None:
            self._ui.kill()
