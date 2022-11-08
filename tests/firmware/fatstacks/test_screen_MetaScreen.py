from unittest import TestCase
from unittest.mock import MagicMock

from ragger.firmware.fatstacks import MetaScreen


class TestMetaScreen(TestCase):

    def setUp(self):
        self.layout = MagicMock()

        class Test(metaclass=MetaScreen):
            layout_one = self.layout

        self.cls = Test
        self.assertEqual(self.layout.call_count, 0)

    def test___init__(self):
        client, firmware = MagicMock(), MagicMock()
        test = self.cls(client, firmware)
        self.assertEqual(self.layout.call_count, 1)
        self.assertEqual(self.layout.call_args, ((client, firmware), ))
        self.assertEqual(test.one, self.layout())
