"""
Copyright 2026 Ledger SAS

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

from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from ledgered.devices import Device

from ragger.backend import BackendInterface
from ragger.utils import Crop

from .instruction import BaseNavInsID, NavIns
from .navigator import InstructionType, Navigator


class ManualNavigator(Navigator):
    """
    Navigator leaving every action on the device to the user.

    While an asynchronous APDU exchange is pending, the navigation methods return
    immediately: the test then blocks on the APDU response until the user ends the flow.
    Otherwise, the expected navigation is printed and the user confirms it is done.
    """

    def __init__(self, backend: BackendInterface, device: Device, golden_run: bool = False):
        super().__init__(backend, device, {}, golden_run)

    @staticmethod
    def _describe(instructions: Sequence[InstructionType]) -> str:
        names = []
        for ins in instructions:
            if isinstance(ins, NavIns):
                args = ", ".join(str(a) for a in ins.args)
                names.append(f"{ins.id.name}({args})" if args else ins.id.name)
            elif isinstance(ins, BaseNavInsID):
                names.append(ins.name)
            else:
                names.append(str(ins))
        return ", ".join(names)

    @staticmethod
    def _open_tty() -> TextIO | None:
        try:
            return open("/dev/tty", "r+")
        except OSError:
            return None

    def _wait_user(self, action: str) -> None:
        if self._backend.is_async_exchange_pending:
            return
        message = f"\n[no-nav] Perform on the device: {action}\n[no-nav] Then press Enter to continue..."
        tty = self._open_tty()
        if tty is None:
            # Requires pytest '-s' for stdin to be readable
            input(message)
            return
        with tty:
            tty.write(message)
            tty.flush()
            tty.readline()

    def navigate_and_compare(
        self,
        path: Path | None,
        test_case_name: Path | str | None,
        instructions: Sequence[InstructionType],
        timeout: float = 10.0,
        screen_change_before_first_instruction: bool = True,
        screen_change_after_last_instruction: bool = True,
        snap_start_idx: int = 0,
    ) -> None:
        self._wait_user(self._describe(instructions))

    def navigate_until_snap(
        self,
        navigate_instruction: InstructionType,
        validation_instruction: InstructionType,
        path: Path,
        test_case_name: Path | str,
        start_img_name: str,
        last_img_name: str,
        take_snaps: bool = True,
        timeout: int = 30,
        crop_first: Crop | None = None,
        crop_last: Crop | None = None,
    ) -> int:
        self._wait_user(
            f"{self._describe([navigate_instruction])} until snapshot '{last_img_name}', "
            f"then {self._describe([validation_instruction])}"
        )
        return 0

    def navigate_until_text_and_compare(
        self,
        navigate_instruction: InstructionType,
        validation_instructions: Sequence[InstructionType],
        text: str,
        path: Path | None = None,
        test_case_name: Path | str | None = None,
        timeout: int = 300,
        screen_change_before_first_instruction: bool = True,
        screen_change_after_last_instruction: bool = True,
        snap_start_idx: int = 0,
    ) -> None:
        self._wait_user(
            f"{self._describe([navigate_instruction])} until text '{text}', then {self._describe(validation_instructions)}"
        )

    def navigate_until_text(
        self,
        navigate_instruction: InstructionType,
        validation_instructions: Sequence[InstructionType],
        text: str,
        timeout: int = 300,
        screen_change_before_first_instruction: bool = True,
        screen_change_after_last_instruction: bool = True,
        snap_start_idx: int = 0,
    ) -> None:
        self.navigate_until_text_and_compare(navigate_instruction, validation_instructions, text)
