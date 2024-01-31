from functools import partial
from unittest import TestCase

from ragger.navigator.stax_navigator import StaxNavigator
from ragger.backend import LedgerCommBackend, LedgerWalletBackend, SpeculosBackend
from ragger.firmware import Firmware


class TestStaxNavigator(TestCase):

    def test___init__ok(self):
        for backend_cls in [
                partial(SpeculosBackend, "some app"), LedgerCommBackend, LedgerWalletBackend
        ]:
            backend = backend_cls(Firmware.STAX)
            StaxNavigator(backend, Firmware.STAX)

    def test___init__nok(self):
        with self.assertRaises(ValueError):
            StaxNavigator("whatever", Firmware.NANOS)
