import struct
from unittest import TestCase
from unittest.mock import MagicMock

from ragger import Firmware, ExceptionRAPDU
from ragger.backend import BackendInterface
from ragger.backend.interface import RaisePolicy


class DummyBackend(BackendInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock = MagicMock()
    def __enter__(self): yield self
    def __exit__(self, *args, **kwargs): pass
    def both_click(self): self.mock.both_click()
    def right_click(self): self.mock.right_click()
    def left_click(self): self.mock.left_click()
    def exchange_async_raw(self, *args, **kwargs): return self.mock.exchange_async_raw(*args, **kwargs)
    def exchange_raw(self, *args, **kwargs): return self.mock.exchange_raw(*args, **kwargs)
    def receive(self): return self.mock.receive()
    def send_raw(self, *args, **kwargs): self.mock.send_raw(*args, **kwargs)


class TestBackendInterface(TestCase):

    def setUp(self):
        self.firmware = Firmware("nanos", "2.0.1")
        self.errors = (ExceptionRAPDU(0x8888, "ERROR1"),
                       ExceptionRAPDU(0x7777, "ERROR2"))
        self.valid_statuses = (0x9000, 0x9001, 0x9002)
        self.backend = DummyBackend(self.firmware)

    def test_init(self):
        self.assertEqual(self.backend.firmware, self.firmware)
        self.assertIsNone(self.backend.last_async_response)

        backend = DummyBackend(self.firmware)
        self.assertEqual(backend.get_raise_policy(), RaisePolicy.RAISE_ALL_BUT_0x9000)
        backend.set_raise_policy(RaisePolicy.RAISE_ALL)
        self.assertEqual(backend.get_raise_policy(), RaisePolicy.RAISE_ALL)
        backend.set_raise_policy(RaisePolicy.RAISE_ALL_BUT_0x9000)

    def test_send(self):
        cla, ins, p1, p2 = 1, 2, 3, 4
        expected = struct.pack(">BBBBB", cla, ins, p1, p2, 0)
        self.assertFalse(self.backend.mock.send_raw.called)
        self.backend.send(cla, ins, p1, p2)
        self.assertTrue(self.backend.mock.send_raw.called)
        self.assertEqual(self.backend.mock.send_raw.call_args,
                         ((expected,),))

    def test_exchange(self):
        cla, ins, p1, p2 = 1, 2, 3, 4
        expected = struct.pack(">BBBBB", cla, ins, p1, p2, 0)
        self.assertFalse(self.backend.mock.send_raw.called)
        result = self.backend.exchange(cla, ins, p1, p2)
        self.assertTrue(self.backend.mock.exchange_raw.called)
        self.assertEqual(self.backend.mock.exchange_raw.call_args,
                         ((expected,),))
        self.assertEqual(result, self.backend.mock.exchange_raw())

    def test_exchange_async(self):
        cla, ins, p1, p2 = 1, 2, 3, 4
        expected = struct.pack(">BBBBB", cla, ins, p1, p2, 0)
        self.assertFalse(self.backend.mock.send_raw.called)
        with self.backend.exchange_async(cla, ins, p1, p2):
            pass
        self.assertTrue(self.backend.mock.exchange_async_raw.called)
        self.assertEqual(self.backend.mock.exchange_async_raw.call_args,
                         ((expected,),))
