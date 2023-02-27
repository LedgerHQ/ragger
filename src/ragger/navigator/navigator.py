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
from enum import auto, Enum
from pathlib import Path
from time import time
from typing import Any, Callable, Dict, List, Optional, Union

from ragger.backend import BackendInterface, SpeculosBackend
from ragger.firmware import Firmware
from ragger.utils import Crop


class NavInsID(Enum):
    WAIT = auto()

    # Navigation instructions for Nano devices
    RIGHT_CLICK = auto()
    LEFT_CLICK = auto()
    BOTH_CLICK = auto()

    # Navigation instructions for Stax devices
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
    USE_CASE_SETTINGS_PREVIOUS = auto()
    USE_CASE_SETTINGS_NEXT = auto()
    USE_CASE_SUB_SETTINGS_EXIT = auto()
    USE_CASE_SUB_SETTINGS_PREVIOUS = auto()
    USE_CASE_SUB_SETTINGS_NEXT = auto()
    USE_CASE_CHOICE_CONFIRM = auto()
    USE_CASE_CHOICE_REJECT = auto()
    USE_CASE_STATUS_WAIT = auto()
    USE_CASE_STATUS_DISMISS = auto()
    USE_CASE_REVIEW_TAP = auto()
    USE_CASE_REVIEW_PREVIOUS = auto()
    USE_CASE_REVIEW_REJECT = auto()
    USE_CASE_REVIEW_CONFIRM = auto()
    USE_CASE_VIEW_DETAILS_EXIT = auto()
    USE_CASE_VIEW_DETAILS_PREVIOUS = auto()
    USE_CASE_VIEW_DETAILS_NEXT = auto()
    USE_CASE_ADDRESS_CONFIRMATION_TAP = auto()
    USE_CASE_ADDRESS_CONFIRMATION_EXIT_QR = auto()
    USE_CASE_ADDRESS_CONFIRMATION_CONFIRM = auto()
    USE_CASE_ADDRESS_CONFIRMATION_CANCEL = auto()


class NavIns:

    def __init__(self, id: NavInsID, args=(), kwargs: Dict[str, Any] = {}):
        self.id = id
        self.args = args
        self.kwargs = kwargs


class Navigator(ABC):

    GOLDEN_INSTRUCTION_SLEEP_MULTIPLIER_FIRST = 2
    GOLDEN_INSTRUCTION_SLEEP_MULTIPLIER_MIDDLE = 5
    GOLDEN_INSTRUCTION_SLEEP_MULTIPLIER_LAST = 2

    def __init__(self,
                 backend: BackendInterface,
                 firmware: Firmware,
                 callbacks: Dict[NavInsID, Callable],
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

    def _init_snaps_temp_dir(self, path: Path, test_case_name: Path, start_idx: int = 0) -> Path:
        snaps_tmp_path = self._get_snaps_dir_path(path, test_case_name, False)
        if snaps_tmp_path.exists():
            for file in snaps_tmp_path.iterdir():
                # Remove all files in format "index.png" with index >= start_idx
                if not file.name.endswith(".png"):
                    continue
                file_idx_str = file.name.replace(".png", "")
                if not file_idx_str.isnumeric():
                    continue
                file_idx = int(file_idx_str)
                if file_idx >= start_idx:
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

    def add_callback(self, ins_id: NavInsID, callback: Callable, override: bool = True) -> None:
        """
        Register a new callback.

        :param ins_id: The navigation instruction ID which will trigger the callback
        :type ins_id: NavInsID
        :param callback: The callback to call
        :type callback: Callable
        :param override: Replace an existing callback if the navigation instruction ID already
                         exists. Defaults to `True`
        :type override: bool

        :raises KeyError: If the navigation instruction ID already exists and `override` is set to
                          False

        :return: None
        :rtype: NoneType
        """
        if not override and ins_id in self._callbacks:
            raise KeyError(f"Navigation instruction ID '{ins_id}' already exists in the "
                           "registered callbacks")
        self._callbacks[ins_id] = callback

    def navigate(self, instructions: List[Union[NavIns, NavInsID]]):
        """
        Navigate on the device according to a set of navigation instructions provided.

        :param instructions: Set of navigation instructions. Navigation instruction IDs are also
                             accepted, and will be converted into navigation instruction (without
                             any argument)
        :type instructions: List[Union[NavIns, NavInsID]]

        :raises NotImplementedError: If the navigation instruction is not implemented.

        :return: None
        :rtype: NoneType
        """
        for instruction in instructions:
            if isinstance(instruction, NavInsID):
                instruction = NavIns(instruction)
            if instruction.id not in self._callbacks:
                raise NotImplementedError()
            self._callbacks[instruction.id](*instruction.args, **instruction.kwargs)

    def navigate_and_compare(self,
                             path: Optional[Path],
                             test_case_name: Optional[Path],
                             instructions: List[Union[Union[NavIns, NavInsID]]],
                             timeout: float = 10.0,
                             screen_change_before_first_instruction: bool = True,
                             screen_change_after_last_instruction: bool = True,
                             snap_start_idx: int = 0) -> None:
        """
        Navigate on the device according to a set of navigation instructions
        provided then compare each step snapshot with "golden images".

        :param path: Absolute path to the snapshots directory.
        :type path: Optional[Path]
        :param test_case_name: Relative path to the test case snapshots directory (from path).
        :type test_case_name: Optional[Path]
        :param instructions: Set of navigation instructions. Navigation instruction IDs are also
                             accepted.
        :type instructions: List[Union[NavIns, NavInsID]]
        :param timeout: Timeout for each navigation step.
        :type timeout: int
        :param screen_change_before_first_instruction: Wait for a screen change before first
                                                       instruction, like a confirmation screen
                                                       triggered through APDUs.
        :type screen_change_before_first_instruction: bool
        :param screen_change_after_last_instruction: Wait for a screen change after last instruction.
        :type screen_change_after_last_instruction: bool
        :param snap_start_idx: Index of the first snap for this navigation.
        :type snap_start_idx: int

        :raises ValueError: If one of the snapshots does not match.

        :return: None
        :rtype: NoneType
        """
        snaps_tmp_path = None
        snaps_golden_path = None
        if path and test_case_name:
            snaps_tmp_path = self._init_snaps_temp_dir(path, test_case_name, snap_start_idx)
            snaps_golden_path = self._check_snaps_dir_path(path, test_case_name, True)

        if screen_change_before_first_instruction:
            self._backend.wait_for_screen_change(timeout)

        # First navigate to the last step and take snapshots of every screen in the flow.
        for idx, instruction in enumerate(instructions):
            if snaps_tmp_path and snaps_golden_path:
                self._compare_snap(snaps_tmp_path, snaps_golden_path, idx + snap_start_idx)

            self.navigate([instruction])

            if idx != len(instructions) - 1:
                self._backend.wait_for_screen_change(timeout)

        if screen_change_after_last_instruction:
            self._backend.wait_for_screen_change(timeout)

            # Compare last screen snapshot
            if snaps_tmp_path and snaps_golden_path:
                self._compare_snap(snaps_tmp_path, snaps_golden_path,
                                   len(instructions) + snap_start_idx)

    def navigate_until_snap(self,
                            navigate_instruction: Union[NavIns, NavInsID],
                            validation_instruction: Union[NavIns, NavInsID],
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
                                     Navigation instruction ID is also accepted.
        :type navigate_instruction: Union[NavIns, NavInsID]
        :param validation_instruction: Navigation instruction to be performed once last snapshot is found.
                                       Navigation instruction ID is also accepted.
        :type validation_instruction: Union[NavIns, NavInsID]
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

    def navigate_until_text_and_compare(self,
                                        navigate_instruction: Union[NavIns, NavInsID],
                                        validation_instructions: List[Union[NavIns, NavInsID]],
                                        text: str,
                                        path: Optional[Path] = None,
                                        test_case_name: Optional[Path] = None,
                                        timeout: int = 30,
                                        screen_change_before_first_instruction: bool = True,
                                        screen_change_after_last_instruction: bool = True) -> None:
        """
        Navigate until some text is found on the screen content displayed then
        compare each step snapshot with "golden images".

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :param path: Absolute path to the snapshots directory.
        :type path: Path
        :param test_case_name: Relative path to the test case snapshots directory (from path).
        :type test_case_name: Path
        :param navigate_instruction: Navigation instruction to be performed until the text is found.
                                     Navigation instruction ID is also accepted.
        :type navigate_instruction: Union[NavIns, NavInsID]
        :param validation_instructions: Navigation instructions to be performed once the text is found.
                                        Navigation instruction IDs are also accepted.
        :type validation_instructions: List[Union[NavIns, NavInsID]]
        :param text: Text string to look for.
        :type text: str
        :param timeout: Timeout for the whole navigation loop.
        :type timeout: int
        :param screen_change_before_first_instruction: Wait for a screen change before first instruction.
        :type screen_change_before_first_instruction: bool
        :param screen_change_after_last_instruction: Wait for a screen change after last instruction.
        :type screen_change_after_last_instruction: bool

        :raises TimeoutError: If the text is not found.

        :return: None
        :rtype: NoneType
        """
        idx = 0
        snaps_tmp_path = None
        snaps_golden_path = None

        if path and test_case_name:
            snaps_tmp_path = self._init_snaps_temp_dir(path, test_case_name)
            snaps_golden_path = self._check_snaps_dir_path(path, test_case_name, True)

        if not isinstance(self._backend, SpeculosBackend):
            # TODO remove this once the proper behavior of other backends is implemented.
            return

        start = time()

        if screen_change_before_first_instruction:
            self._backend.wait_for_screen_change(timeout)

        # Navigate until the text specified in argument is found.
        while True:
            if snaps_tmp_path and snaps_golden_path:
                self._compare_snap(snaps_tmp_path, snaps_golden_path, idx)

            if not self._backend.compare_screen_with_text(text):
                # Go to the next screen.
                self.navigate([navigate_instruction])
                idx += 1
            else:
                # Validation screen text found, exit the loop
                break

            # Global navigation loop timeout in case the text is never found.
            remaining = timeout - (time() - start)
            if (remaining < 0):
                raise TimeoutError(f"Timeout waiting for text {text}")

            self._backend.wait_for_screen_change(remaining)

        # Perform navigation validation instructions in an "navigate_and_compare" way.
        if validation_instructions:
            remaining = timeout - (time() - start)
            self.navigate_and_compare(
                path,
                test_case_name,
                validation_instructions,
                timeout=remaining,
                screen_change_before_first_instruction=False,
                screen_change_after_last_instruction=screen_change_after_last_instruction,
                snap_start_idx=idx)

    def navigate_until_text(self,
                            navigate_instruction: Union[NavIns, NavInsID],
                            validation_instructions: List[Union[NavIns, NavInsID]],
                            text: str,
                            timeout: int = 30,
                            screen_change_before_first_instruction: bool = True,
                            screen_change_after_last_instruction: bool = True) -> None:
        """
        Navigate until some text is found on the screen content displayed.

        This method may be left void on backends connecting to physical devices,
        where a physical interaction must be performed instead.
        This will prevent the instrumentation to fail (the void method won't
        raise `NotImplementedError`), but the instrumentation flow will probably
        get stuck (on further call to `receive` for instance) until the expected
        action is performed on the device.

        :param navigate_instruction: Navigation instruction to be performed until the text is found.
                                     Navigation instruction ID is also accepted.
        :type navigate_instruction: Union[NavIns, NavInsID]
        :param validation_instructions: Navigation instructions to be performed once the text is found.
                                        Navigation instruction IDs are also accepted.
        :type validation_instructions: List[Union[NavIns, NavInsID]]
        :param text: Text string to look for.
        :type text: str
        :param timeout: Timeout for the whole navigation loop.
        :type timeout: int
        :param screen_change_before_first_instruction: Wait for a screen change before first instruction.
        :type screen_change_before_first_instruction: bool
        :param screen_change_after_last_instruction: Wait for a screen change after last instruction.
        :type screen_change_after_last_instruction: bool

        :raises TimeoutError: If the text is not found.

        :return: None
        :rtype: NoneType
        """
        self.navigate_until_text_and_compare(navigate_instruction, validation_instructions, text,
                                             None, None, timeout,
                                             screen_change_before_first_instruction,
                                             screen_change_after_last_instruction)
