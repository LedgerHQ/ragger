from unittest import TestCase
from unittest.mock import MagicMock, patch

from ragger.firmware.stax.layouts import _Layout


class Test_Layout(TestCase):

    def test___init__(self):
        client = MagicMock()
        firmware = MagicMock()
        positions = MagicMock()
        with patch("ragger.firmware.stax.layouts.POSITIONS", {_Layout.__name__: positions}):
            layout = _Layout(client, firmware)
            self.assertEqual(layout.firmware, firmware)
            self.assertEqual(layout.client, client)
            self.assertEqual(layout.positions, positions)
