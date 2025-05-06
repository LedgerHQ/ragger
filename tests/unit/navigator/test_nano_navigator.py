from functools import partial
from unittest import TestCase
from ledgered.devices import DeviceType, Devices

from ragger.navigator.nano_navigator import NanoNavigator
from ragger.backend import LedgerCommBackend, LedgerWalletBackend, SpeculosBackend


class TestNanoNavigator(TestCase):

    def test___init__ok(self):
        for backend_cls in [
                partial(SpeculosBackend, "some app"), LedgerCommBackend, LedgerWalletBackend
        ]:
            backend = backend_cls(Devices.get_by_type(DeviceType.NANOS))
            NanoNavigator(backend, Devices.get_by_type(DeviceType.NANOS))

    def test___init__nok(self):
        with self.assertRaises(ValueError):
            NanoNavigator("whatever", Devices.get_by_type(DeviceType.STAX))
