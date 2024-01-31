from functools import partial
from unittest import TestCase

from ragger.navigator.nano_navigator import NanoNavigator
from ragger.backend import LedgerCommBackend, LedgerWalletBackend, SpeculosBackend
from ragger.firmware import Firmware


class TestNanoNavigator(TestCase):

    def test___init__ok(self):
        for backend_cls in [
                partial(SpeculosBackend, "some app"), LedgerCommBackend, LedgerWalletBackend
        ]:
            backend = backend_cls(Firmware.NANOS)
            NanoNavigator(backend, Firmware.NANOS)

    def test___init__nok(self):
        with self.assertRaises(ValueError):
            NanoNavigator("whatever", Firmware.STAX)
