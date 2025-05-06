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
