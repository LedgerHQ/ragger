from pathlib import Path
from typing import Optional, Sequence
from enum import Enum, auto

from ragger.firmware import Firmware
from .navigator import InstructionType, Navigator, NavInsID


class UseCase(Enum):
    TX_REVIEW = auto()
    ADDRESS_CONFIRMATION = auto()


class NavigationScenarioData:
    navigation: NavInsID
    validation: Sequence[InstructionType]
    pattern: str

    def __init__(self, device: Firmware, use_case: UseCase, approve: bool):
        if device.is_nano:
            self.navigation = NavInsID.RIGHT_CLICK
            self.validation = [NavInsID.BOTH_CLICK]
            self.pattern = "^Approve$" if approve else "^Reject$"

        elif device in [Firmware.STAX, Firmware.FLEX]:
            self.navigation = NavInsID.SWIPE_CENTER_TO_LEFT

            if use_case == UseCase.ADDRESS_CONFIRMATION:
                if approve:
                    self.validation = [NavInsID.USE_CASE_ADDRESS_CONFIRMATION_CONFIRM]
                else:
                    self.validation = [NavInsID.USE_CASE_ADDRESS_CONFIRMATION_CANCEL]
                self.pattern = "^Confirm$"

            elif use_case == UseCase.TX_REVIEW:
                if approve:
                    self.validation = [NavInsID.USE_CASE_REVIEW_CONFIRM]
                else:
                    self.validation = [
                        NavInsID.USE_CASE_REVIEW_REJECT, NavInsID.USE_CASE_CHOICE_CONFIRM
                    ]
                self.pattern = "^Hold to sign$"

            else:
                raise NotImplementedError("Unknown use case")

            # Dismiss the result modal in all cases
            self.validation += [NavInsID.USE_CASE_STATUS_DISMISS]

        else:
            raise NotImplementedError("Unknown device")


class NavigateWithScenario:

    def __init__(self, navigator: Navigator, device: Firmware, test_name: str,
                 screenshot_path: Path):
        self.navigator = navigator
        self.device = device
        self.test_name = test_name
        self.screenshot_path = screenshot_path

    def _navigate_with_scenario(self,
                                scenario: NavigationScenarioData,
                                path: Optional[Path] = None,
                                test_name: Optional[str] = None,
                                custom_screen_text: Optional[str] = None,
                                do_comparison: bool = True):
        if custom_screen_text is not None:
            scenario.pattern = custom_screen_text

        if do_comparison:
            self.navigator.navigate_until_text_and_compare(
                navigate_instruction=scenario.navigation,
                validation_instructions=scenario.validation,
                text=scenario.pattern,
                path=path if path else self.screenshot_path,
                test_case_name=test_name if test_name else self.test_name)
        else:
            self.navigator.navigate_until_text(navigate_instruction=scenario.navigation,
                                               validation_instructions=scenario.validation,
                                               text=scenario.pattern)

    def review_approve(self,
                       path: Optional[Path] = None,
                       test_name: Optional[str] = None,
                       custom_screen_text: Optional[str] = None,
                       do_comparison: bool = True):
        scenario = NavigationScenarioData(self.device, UseCase.TX_REVIEW, approve=True)
        self._navigate_with_scenario(scenario, path, test_name, custom_screen_text, do_comparison)

    def review_reject(self,
                      path: Optional[Path] = None,
                      test_name: Optional[str] = None,
                      custom_screen_text: Optional[str] = None,
                      do_comparison: bool = True):
        scenario = NavigationScenarioData(self.device, UseCase.TX_REVIEW, approve=False)
        self._navigate_with_scenario(scenario, path, test_name, custom_screen_text, do_comparison)

    def address_review_approve(self,
                               path: Optional[Path] = None,
                               test_name: Optional[str] = None,
                               custom_screen_text: Optional[str] = None,
                               do_comparison: bool = True):
        scenario = NavigationScenarioData(self.device, UseCase.ADDRESS_CONFIRMATION, approve=True)
        self._navigate_with_scenario(scenario, path, test_name, custom_screen_text, do_comparison)

    def address_review_reject(self,
                              path: Optional[Path] = None,
                              test_name: Optional[str] = None,
                              custom_screen_text: Optional[str] = None,
                              do_comparison: bool = True):
        scenario = NavigationScenarioData(self.device, UseCase.ADDRESS_CONFIRMATION, approve=False)
        self._navigate_with_scenario(scenario, path, test_name, custom_screen_text, do_comparison)
