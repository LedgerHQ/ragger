from ledgered.devices import DeviceType, Devices
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock

from ragger.navigator import NavigateWithScenario


class TestNavigationScenario(TestCase):

    def setUp(self):
        self.directory = TemporaryDirectory()
        self.backend = MagicMock()
        self.device = Devices.get_by_type(DeviceType.NANOS)
        self.callbacks = dict()
        self.navigator = MagicMock()
        self.navigate_with_scenario = NavigateWithScenario(self.backend, self.navigator,
                                                           self.device, "test_name", self.directory)

    def tearDown(self):
        self.directory.cleanup()

    @property
    def pathdir(self) -> Path:
        return Path(self.directory.name)

    def test_navigation_scenario(self):
        self.assertIsNone(self.navigate_with_scenario.review_approve())
        self.assertIsNone(self.navigate_with_scenario.review_reject())
        self.assertIsNone(self.navigate_with_scenario.address_review_approve())
        self.assertIsNone(self.navigate_with_scenario.address_review_reject())

    def test_review_approve_with_spinner_nano(self):
        """Test that review_approve_with_spinner passes screen_change_after_last_instruction=False
        to the navigator and calls backend.wait_for_text_on_screen with the spinner pattern."""
        spinner_text = "Processing..."
        self.navigate_with_scenario.review_approve_with_spinner(spinner_text)

        # The navigator should have been called with screen_change_after_last_instruction=False
        self.navigator.navigate_until_text_and_compare.assert_called_once()
        call_kwargs = self.navigator.navigate_until_text_and_compare.call_args
        self.assertFalse(
            call_kwargs.kwargs.get(
                'screen_change_after_last_instruction',
                call_kwargs[1].get('screen_change_after_last_instruction', True)
                if len(call_kwargs) > 1 else True))

        # The backend should have been called with the spinner text
        self.backend.wait_for_text_on_screen.assert_called_once_with(spinner_text)

    def test_review_approve_with_spinner_no_comparison(self):
        """Test that review_approve_with_spinner with do_comparison=False uses navigate_until_text
        with screen_change_after_last_instruction=False and calls wait_for_text_on_screen."""
        spinner_text = "Signing..."
        self.navigate_with_scenario.review_approve_with_spinner(spinner_text, do_comparison=False)

        # navigate_until_text should have been called (not navigate_until_text_and_compare)
        self.navigator.navigate_until_text_and_compare.assert_not_called()
        self.navigator.navigate_until_text.assert_called_once()
        call_kwargs = self.navigator.navigate_until_text.call_args
        self.assertFalse(
            call_kwargs.kwargs.get(
                'screen_change_after_last_instruction',
                call_kwargs[1].get('screen_change_after_last_instruction', True)
                if len(call_kwargs) > 1 else True))

        # The backend should have been called with the spinner text
        self.backend.wait_for_text_on_screen.assert_called_once_with(spinner_text)

    def test_review_approve_with_spinner_touchable(self):
        """Test spinner behavior on a touchable device (Stax)."""
        device = Devices.get_by_type(DeviceType.STAX)
        navigate_with_scenario = NavigateWithScenario(self.backend, self.navigator, device,
                                                      "test_name", self.directory)
        spinner_text = "Please wait..."
        navigate_with_scenario.review_approve_with_spinner(spinner_text)

        # The navigator should have been called with screen_change_after_last_instruction=False
        self.navigator.navigate_until_text_and_compare.assert_called_once()
        call_kwargs = self.navigator.navigate_until_text_and_compare.call_args
        self.assertFalse(
            call_kwargs.kwargs.get(
                'screen_change_after_last_instruction',
                call_kwargs[1].get('screen_change_after_last_instruction', True)
                if len(call_kwargs) > 1 else True))

        # The backend should have been called with the spinner text
        self.backend.wait_for_text_on_screen.assert_called_once_with(spinner_text)
