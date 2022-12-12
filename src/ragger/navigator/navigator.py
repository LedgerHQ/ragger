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
from abc import ABC
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional, Dict, Any
from time import sleep, time

from ragger.backend import BackendInterface, SpeculosBackend
from ragger.firmware import Firmware
from ragger.utils import Crop


class NavInsID(Enum):
    WAIT = auto()

    # Navigation instructions for Nano devices
    RIGHT_CLICK = auto()
    LEFT_CLICK = auto()
    BOTH_CLICK = auto()

    # Navigation instructions for Fatstacks devices
    TOUCH = auto()
    # possible headers
    RIGHT_HEADER_TAP = auto()
    EXIT_HEADER_TAP = auto()
    INFO_HEADER_TAP = auto()
    LEFT_HEADER_TAP = auto()
    NAVIGATION_HEADER_TAP = auto()
    # possible centers
    CHOICE_CHOOSE = auto()
    SUGGESTION_CHOOSE = auto()
    TAPPABLE_CENTER_TAP = auto()
    KB_LETTER_ONLY_WRITE = auto()
    KB_LETTERS_WRITE = auto()
    KB_SPECIAL_CHAR_1_WRITE = auto()
    KB_SPECIAL_CHAR_2_WRITE = auto()
    # possible footers
    CENTERED_FOOTER_TAP = auto()
    CANCEL_FOOTER_TAP = auto()
    EXIT_FOOTER_TAP = auto()
    INFO_FOOTER_TAP = auto()
    # use cases
    USE_CASE_HOME_INFO = auto()
    USE_CASE_HOME_SETTINGS = auto()
    USE_CASE_HOME_QUIT = auto()
    USE_CASE_SETTINGS_SINGLE_PAGE_EXIT = auto()
    USE_CASE_SETTINGS_MULTI_PAGE_EXIT = auto()
    USE_CASE_SETTINGS_BACK = auto()
    USE_CASE_SETTINGS_NEXT = auto()
    USE_CASE_SUB_SETTINGS_EXIT = auto()
    USE_CASE_SUB_SETTINGS_BACK = auto()
    USE_CASE_SUB_SETTINGS_NEXT = auto()
    USE_CASE_CHOICE_CONFIRM = auto()
    USE_CASE_CHOICE_REJECT = auto()
    USE_CASE_STATUS_WAIT = auto()
    USE_CASE_REVIEW_TAP = auto()
    USE_CASE_REVIEW_BACK = auto()
    USE_CASE_REVIEW_REJECT = auto()
    USE_CASE_REVIEW_CONFIRM = auto()
    USE_CASE_VIEW_DETAILS_EXIT = auto()
    USE_CASE_VIEW_DETAILS_BACK = auto()
    USE_CASE_VIEW_DETAILS_NEXT = auto()
    USE_CASE_ADDRESS_CONFIRMATION_EXIT_QR = auto()
    USE_CASE_ADDRESS_CONFIRMATION_CONFIRM = auto()
    USE_CASE_ADDRESS_CONFIRMATION_CANCEL = auto()


class NavIns:

    def __init__(self, id: NavInsID, args=(), kwargs: Dict[str, Any] = {}):
        self.id = id
        self.args = args
        self.kwargs = kwargs


class Navigator(ABC):

    def __init__(self,
                 backend: BackendInterface,
                 firmware: Firmware,
                 callbacks: Dict[NavInsID, Any],
                 golden_run: bool = False):
        """Initializes the Backend

        :param firmware: Which Backend will be managed
        :type firmware: Backend
        :param firmware: Which Firmware will be managed
        :type firmware: Firmware
        :param callbacks: Callbacks to use to navigate
        :type callbacks: Firmware
        :param golden_run: Allows to generate golden snapshots
        :type golden_run: bool
        """
        self._backend = backend
        self._firmware = firmware
        self._callbacks = callbacks
        self._golden_run = golden_run

    def _get_snaps_dir_path(self, path: Path, test_case_name: Path, is_golden: bool) -> Path:
        if is_golden:
            subdir = "snapshots"
        else:
            subdir = "snapshots-tmp"
        return path / subdir / self._firmware.device / test_case_name

    def _check_snaps_dir_path(self, path: Path, test_case_name: Path, is_golden: bool) -> Path:
        dir_path = self._get_snaps_dir_path(path, test_case_name, is_golden)
        if not dir_path.is_dir():
            if self._golden_run:
                dir_path.mkdir(parents=True)
            else:
                raise ValueError(f"Golden snapshots directory ({dir_path}) does not exist.")
        return dir_path

    def _init_snaps_temp_dir(self, path: Path, test_case_name: Path) -> Path:
        snaps_tmp_path = self._get_snaps_dir_path(path, test_case_name, False)
        if snaps_tmp_path.exists():
            for file in snaps_tmp_path.iterdir():
                file.unlink()
        else:
            snaps_tmp_path.mkdir(parents=True)
        return snaps_tmp_path

    def _get_snap_path(self, path: Path, index: int) -> Path:
        return path / f"{str(index).zfill(5)}.png"

    def _compare_snap_with_timeout(self,
                                   path: Path,
                                   timeout_s: float = 5.0,
                                   crop: Optional[Crop] = None,
                                   tmp_snap_path: Optional[Path] = None) -> bool:
        start = time()
        now = start
        while not (now - start > timeout_s):
            if self._backend.compare_screen_with_snapshot(path, crop, tmp_snap_path=tmp_snap_path):
                return True
            now = time()
        return False

    def _compare_snap(self, snaps_tmp_path: Path, snaps_golden_path: Path, index: int):
        golden = self._get_snap_path(snaps_golden_path, index)
        tmp = self._get_snap_path(snaps_tmp_path, index)

        assert self._backend.compare_screen_with_snapshot(
            golden, tmp_snap_path=tmp,
            golden_run=self._golden_run), f"Screen does not match golden {tmp}."

    def navigate(self, instructions: List[NavIns]):
        """
        Navigate on the device according to a set of navigation instructions provided.

        :param instructions: Set of navigation instructions.
        :type instructions: List[NavIns]

        :raises NotImplementedError: If the navigation instruction is not implemented.

        :return: None
        :rtype: NoneType
        """
        for instruction in instructions:
            if instruction.id not in self._callbacks:
                raise NotImplementedError
            self._callbacks[instruction.id](*instruction.args, **instruction.kwargs)

    def navigate_and_compare(self,
                             path: Path,
                             test_case_name: Path,
                             instructions: List[NavIns],
                             first_instruction_wait: float = 1.0,
                             middle_instruction_wait: float = 0.1,
                             last_instruction_wait: float = 0.5) -> None:
        """
        Navigate on the device according to a set of navigation instructions
        provided then compare each step snapshot with "golden images".

        :param path: Absolute path to the snapshots directory.
        :type path: Path
        :param test_case_name: Relative path to the test case snapshots directory (from path).
        :type test_case_name: Path
        :param instructions: List of navigation instructions.
        :type instructions: List[NavIns]
        :param first_instruction_wait: Sleeping time before the first snapshot
        :type first_instruction_wait: float
        :param middle_instruction_wait: Sleeping time between between each navigation instruction
        :type middle_instruction_wait: float
        :param last_instruction_wait: Sleeping time after the last navigation instruction
        :type last_instruction_wait: float

        :raises ValueError: If one of the snapshots do not match.

        :return: None
        :rtype: NoneType
        """
        if self._golden_run:
            # Increase waits when in golden run to be sure that potential processing
            # has been done and next screen has been displayed before continuing.
            # If initial timing was not enough, then it will fail when running without
            # golden run mode and developer will be notified.
            first_instruction_wait *= 2
            middle_instruction_wait *= 5
            last_instruction_wait *= 2
        snaps_tmp_path = self._init_snaps_temp_dir(path, test_case_name)
        snaps_golden_path = self._check_snaps_dir_path(path, test_case_name, True)

        # TODO replace hardcoded wait by Speculos sreen change event wait mechanism
        sleep(first_instruction_wait)

        # First navigate to the last step and take snapshots of every screen in the flow.
        for idx, instruction in enumerate(instructions):
            self._compare_snap(snaps_tmp_path, snaps_golden_path, idx)

            self.navigate([instruction])

            sleep(middle_instruction_wait)

        sleep(last_instruction_wait)

        # Compare last screen snapshot
        self._compare_snap(snaps_tmp_path, snaps_golden_path, len(instructions))

    def navigate_until_snap(self,
                            navigate_instruction: NavIns,
                            validation_instruction: NavIns,
                            path: Path,
                            test_case_name: Path,
                            start_img_name: str,
                            last_img_name: str,
                            take_snaps: bool = True,
                            timeout: int = 30,
                            crop_first: Optional[Crop] = None,
                            crop_last: Optional[Crop] = None) -> int:
        """
        Navigate until snapshot is found.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :param navigate_instruction: Navigation instruction to be performed until last snapshot is found.
        :type navigate_instruction: NavIns
        :param validation_instruction: Navigation instruction to be performed once last snapshot is found.
        :type validation_instruction: NavIns
        :param path: Absolute path to the snapshots directory.
        :type path: Path
        :param test_case_name: Relative path to the test case snapshots directory (from path).
        :type test_case_name: Path
        :param start_img_name: Index of the first snapshot of the navigation flow.
        :type start_img_name: int
        :param last_img_name: Index of the snapshot to look for when navigating.
        :type last_img_name: int
        :param take_snaps: Take temporary snapshots of the screen displayed when navigating.
        :type take_snaps: bool
        :param timeout: Timeout of the navigation loop if last snapshot is not found.
        :type timeout: int
        :param crop_first: Crop (left, upper, right or lower pixels) first snapshot image for comparison
                           (useful if using a generic snapshot).
        :type crop_first: Crop
        :param crop_last: Crop (left, upper, right or lower pixels) last snapshot image for comparison
                          (useful if using a generic snapshot).
        :type crop_last: Crop

        :return: img_idx
        :rtype: int
        """

        if not isinstance(self._backend, SpeculosBackend):
            # When not using Speculos backend, taking snapshots is not possible
            # therefore comparison is not possible too.
            # TODO request user to interact with the device.
            return 0

        snaps_golden_path = self._check_snaps_dir_path(path, test_case_name, True)
        snaps_tmp_path = self._init_snaps_temp_dir(path, test_case_name)

        img_idx = 0
        first_golden_snap = snaps_golden_path / start_img_name
        last_golden_snap = snaps_golden_path / last_img_name

        # Take snapshots if required.
        if take_snaps:
            tmp_snap_path = self._get_snap_path(snaps_tmp_path, img_idx)
        else:
            tmp_snap_path = None

        # Check if the first snapshot is found before going in the navigation loop.
        # It saves time in non-nominal cases where the navigation flow does not start.
        if self._compare_snap_with_timeout(first_golden_snap,
                                           timeout_s=2,
                                           crop=crop_first,
                                           tmp_snap_path=tmp_snap_path):
            start = time()
            # Navigate until the last snapshot specified in argument is found.
            while True:
                if take_snaps:
                    # Take snapshots if required.
                    tmp_snap_path = self._get_snap_path(snaps_tmp_path, img_idx)

                if self._compare_snap_with_timeout(last_golden_snap,
                                                   timeout_s=0.5,
                                                   crop=crop_last,
                                                   tmp_snap_path=tmp_snap_path):
                    break

                now = time()
                # Global navigation loop timeout in case the snapshot is never found.
                if (now - start > timeout):
                    raise TimeoutError(f"Timeout waiting for snap {last_golden_snap}")

                # Go to the next screen.
                self.navigate([navigate_instruction])
                img_idx += 1

            # Validation action when last snapshot is found.
            self.navigate([validation_instruction])

            # Make sure there is a screen update after the final action.
            start = time()
            last_screen_update_timeout = 2
            while self._compare_snap_with_timeout(last_golden_snap, timeout_s=0.5, crop=crop_last):
                now = time()
                if (now - start > last_screen_update_timeout):
                    raise TimeoutError(
                        f"Timeout waiting for screen change after last snapshot : {last_golden_snap}"
                    )
        else:
            raise ValueError(f"Could not find first snapshot {first_golden_snap}")
        return img_idx
