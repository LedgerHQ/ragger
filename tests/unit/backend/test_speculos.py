from unittest import TestCase

from ragger.backend import SpeculosBackend
from ragger.firmware import Firmware


class TestSpeculosBackend(TestCase):

    def setUp(self):
        self.firmware = Firmware('nanos', '2.1')

    def test___init__ok(self):
        SpeculosBackend("some app", firmware=self.firmware)

    def test___init__args_ok(self):
        SpeculosBackend("some app", firmware=self.firmware, args=["some", "specific", "arguments"])

    def test___init__args_nok(self):
        with self.assertRaises(AssertionError):
            SpeculosBackend("some app", firmware=self.firmware, args="not a list")
