from unittest import TestCase
from unittest.mock import MagicMock, patch

from ragger.firmware.touch.element import Element


class TestElement(TestCase):

    def test___init__(self):
        client = MagicMock()
        device = MagicMock()
        positions = MagicMock()
        with patch("ragger.firmware.touch.element.POSITIONS", {Element.__name__: positions}):
            element = Element(client, device)
            self.assertEqual(element.device, device)
            self.assertEqual(element.client, client)
            self.assertEqual(element.positions, positions[device.type])
