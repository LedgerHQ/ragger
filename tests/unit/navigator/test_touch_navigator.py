from functools import partial
from unittest import TestCase

from ragger.navigator.touch_navigator import TouchNavigator
from ragger.backend import LedgerCommBackend, LedgerWalletBackend, SpeculosBackend
from ragger.firmware import Firmware


class TestTouchNavigator(TestCase):

    def test___init__ok(self):
        for backend_cls in [
                partial(SpeculosBackend, "some app"), LedgerCommBackend, LedgerWalletBackend
        ]:
            backend = backend_cls(Firmware.STAX)
            TouchNavigator(backend, Firmware.STAX)

    def test___init__nok(self):
        with self.assertRaises(ValueError):
            TouchNavigator("whatever", Firmware.NANOS)
