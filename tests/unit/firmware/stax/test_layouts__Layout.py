from unittest import TestCase
from unittest.mock import MagicMock, patch

from ragger.firmware.stax.layouts import _Layout


class Test_Layout(TestCase):

    def test___init__(self):
        client = MagicMock()
        firmware = MagicMock()
        positions = MagicMock()
        with patch("ragger.firmware.stax.layouts.POSITIONS_BY_SDK") as positions_by_sdk:
            positions_by_sdk.__contains__.return_value = [firmware.semantic_version]
            positions_by_sdk.__getitem__.return_value = {_Layout.__name__: positions}

            layout = _Layout(client, firmware)
            self.assertEqual(layout.firmware, firmware)
            self.assertEqual(layout.client, client)
            self.assertEqual(layout.positions, positions)

    def test___init__raises(self):
        firmware = MagicMock()
        firmware.semamtic_version = "this version should not exist"
        with self.assertRaises(AssertionError):
            _Layout(None, firmware)
