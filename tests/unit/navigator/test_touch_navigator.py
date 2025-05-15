from functools import partial
from ledgered.devices import DeviceType, Devices
from unittest import TestCase

from ragger.navigator.touch_navigator import TouchNavigator
from ragger.backend import LedgerCommBackend, LedgerWalletBackend, SpeculosBackend


class TestTouchNavigator(TestCase):

    def test___init__ok(self):
        for backend_cls in [
                partial(SpeculosBackend, "some app"), LedgerCommBackend, LedgerWalletBackend
        ]:
            backend = backend_cls(Devices.get_by_type(DeviceType.STAX))
            TouchNavigator(backend, Devices.get_by_type(DeviceType.STAX))

    def test___init__nok(self):
        with self.assertRaises(ValueError):
            TouchNavigator("whatever", Devices.get_by_type(DeviceType.NANOS))
