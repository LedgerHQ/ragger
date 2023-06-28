from unittest import TestCase

from ragger.backend import SpeculosBackend
from ragger.firmware import Firmware


class TestSpeculosBackend(TestCase):

    def test___init__ok(self):
        SpeculosBackend("some app", firmware=Firmware.NANOS)

    def test___init__args_ok(self):
        SpeculosBackend("some app", firmware=Firmware.NANOS, args=["some", "specific", "arguments"])

    def test___init__args_nok(self):
        with self.assertRaises(AssertionError):
            SpeculosBackend("some app", firmware=Firmware.NANOS, args="not a list")
