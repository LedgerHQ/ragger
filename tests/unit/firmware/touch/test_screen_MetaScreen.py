from unittest import TestCase
from unittest.mock import MagicMock

from ragger.firmware.touch import MetaScreen


class TestMetaScreen(TestCase):

    def setUp(self):
        self.layout = MagicMock()

        class Test(metaclass=MetaScreen):
            layout_one = self.layout

            def __init__(self, client, device, some_argument, other=None):
                self.some = some_argument
                self.other = other

        self.cls = Test
        self.assertEqual(self.layout.call_count, 0)

    def test___init__(self):
        client, device = MagicMock(), MagicMock()
        args = (client, device, "some")
        test = self.cls(*args)
        self.assertEqual(self.layout.call_count, 1)
        self.assertEqual(self.layout.call_args, ((client, device), ))
        self.assertEqual(test.one, self.layout())
        self.assertEqual(test.some, args[-1])
        self.assertIsNone(test.other)
