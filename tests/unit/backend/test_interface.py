import struct
import tempfile
from ledgered.devices import DeviceType, Devices
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

from ragger.error import ExceptionRAPDU
from ragger.backend import BackendInterface
from ragger.backend import RaisePolicy


class DummyBackend(BackendInterface):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock = MagicMock()

    def __enter__(self):
        yield self

    def __exit__(self, *args, **kwargs):
        pass

    def both_click(self):
        self.mock.both_click()

    def right_click(self):
        self.mock.right_click()

    def left_click(self):
        self.mock.left_click()

    def exchange_async_raw(self, *args, **kwargs):
        return self.mock.exchange_async_raw(*args, **kwargs)

    def exchange_raw(self, data: bytes, tick_timeout: int):
        return self.mock.exchange_raw(data, tick_timeout)

    def receive(self):
        return self.mock.receive()

    def send_raw(self, *args, **kwargs):
        self.mock.send_raw(*args, **kwargs)

    def finger_touch(self, *args, **kwargs):
        self.mock.finger_touch(*args, **kwargs)

    def finger_swipe(self, *args, **kwargs):
        self.mock.finger_touch(*args, **kwargs)

    def compare_screen_with_snapshot(self, snap_path, crop=None) -> bool:
        return self.mock.compare_screen_with_snapshot()

    def save_screen_snapshot(self, path) -> None:
        self.mock.save_screen_snapshot()

    def wait_for_home_screen(self, timeout: float = 10.0, context: list = []):
        return self.mock.wait_for_home_screen()

    def wait_for_screen_change(self, timeout: float = 10.0, context: list = []):
        return self.mock.wait_for_screen_change()

    def wait_for_text_on_screen(self, text: str, timeout: float = 10.0) -> None:
        self.mock.wait_for_text_on_screen()

    def wait_for_text_not_on_screen(self, text: str, timeout: float = 10.0) -> None:
        self.mock.wait_for_text_not_on_screen()

    def compare_screen_with_text(self, text: str):
        return self.mock.compare_screen_with_text()

    def get_current_screen_content(self):
        return self.mock.get_current_screen_content()

    def pause_ticker(self) -> None:
        pass

    def resume_ticker(self) -> None:
        pass

    def send_tick(self) -> None:
        pass


class TestBackendInterface(TestCase):

    def setUp(self):
        self.device = Devices.get_by_type(DeviceType.NANOS)
        self.errors = (ExceptionRAPDU(0x8888, "ERROR1"), ExceptionRAPDU(0x7777, "ERROR2"))
        self.valid_statuses = (0x9000, 0x9001, 0x9002)
        self.backend = DummyBackend(device=self.device)

    def test_init(self):
        self.assertEqual(self.backend.device, self.device)
        self.assertIsNone(self.backend.last_async_response)

        # Default value
        self.assertEqual(self.backend.raise_policy, RaisePolicy.RAISE_ALL_BUT_0x9000)

    def test_send(self):
        cla, ins, p1, p2 = 1, 2, 3, 4
        expected = struct.pack(">BBBBB", cla, ins, p1, p2, 0)
        self.assertFalse(self.backend.mock.send_raw.called)
        self.backend.send(cla, ins, p1, p2)
        self.assertTrue(self.backend.mock.send_raw.called)
        self.assertEqual(self.backend.mock.send_raw.call_args, ((expected, ), ))

    def test_exchange(self):
        cla, ins, p1, p2 = 1, 2, 3, 4
        expected = struct.pack(">BBBBB", cla, ins, p1, p2, 0)
        self.assertFalse(self.backend.mock.send_raw.called)
        result = self.backend.exchange(cla, ins, p1, p2)
        self.assertTrue(self.backend.mock.exchange_raw.called)
        self.assertEqual(self.backend.mock.exchange_raw.call_args, ((expected, 5 * 60 * 10), ))
        self.assertEqual(result, self.backend.mock.exchange_raw())

    def test_exchange_async(self):
        cla, ins, p1, p2 = 1, 2, 3, 4
        expected = struct.pack(">BBBBB", cla, ins, p1, p2, 0)
        self.assertFalse(self.backend.mock.send_raw.called)
        with self.backend.exchange_async(cla, ins, p1, p2):
            pass
        self.assertTrue(self.backend.mock.exchange_async_raw.called)
        self.assertEqual(self.backend.mock.exchange_async_raw.call_args, ((expected, ), ))


class TestBackendInterfaceLogging(TestCase):

    def test_log_apdu(self):
        self.device = Devices.get_by_type(DeviceType.NANOS)
        with tempfile.TemporaryDirectory() as td:
            test_file = (Path(td) / "test_log_file.log").resolve()
            self.backend = DummyBackend(device=self.device, log_apdu_file=test_file)
            ref_lines = ["Test logging", "hello world", "Lorem Ipsum"]
            for l in ref_lines:
                self.backend.apdu_logger.info(l)
            with open(test_file, mode='r') as fp:
                read_lines = [l.strip() for l in fp.readlines()]
                self.assertEqual(read_lines, ref_lines)
