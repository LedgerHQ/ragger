from contextlib import contextmanager
from ledgered.devices import DeviceType, Devices
from typing import Generator
from unittest import TestCase
from unittest.mock import MagicMock

from ragger.backend import BackendInterface
from ragger.backend.physical_backend import PhysicalBackend
from ragger.gui import RaggerGUI
from ragger.navigator.instruction import NavInsID
from ragger.utils.structs import RAPDU


class StubPhysicalBackend(PhysicalBackend):

    def __enter__(self):
        pass

    def send_raw(self, data: bytes = b""):
        pass

    def receive(self) -> RAPDU:
        return RAPDU(0x9000, b"")

    def exchange_raw(self, data: bytes = b"") -> RAPDU:
        return RAPDU(0x9000, b"")

    @contextmanager
    def exchange_async_raw(self, data: bytes = b"") -> Generator[None, None, None]:
        yield


class TestPhysicalBackend(TestCase):

    def setUp(self):
        self.device = Devices.get_by_type(DeviceType.NANOS)
        self.backend = StubPhysicalBackend(self.device, with_gui=True)
        # patching the `start` function to avoid triggering a real interface
        self.backend._ui.start = MagicMock()

    def test___init__no_gui(self):
        backend = StubPhysicalBackend(self.device)
        self.assertIsInstance(backend, BackendInterface)
        self.assertIsNone(backend._ui)

    def test__init__with_gui(self):
        self.assertIsInstance(self.backend._ui, RaggerGUI)
        self.assertFalse(self.backend._ui.is_alive())

    def test_init_gui_no_ui(self):
        backend = StubPhysicalBackend(self.device)
        with self.assertRaises(AssertionError):
            backend.init_gui()

    def test_init_gui_with_gui(self):
        self.assertIsNone(self.backend.init_gui())
        self.assertTrue(self.backend._ui.start.called)

    def test_navigation_methods_no_gui_None(self):
        backend = StubPhysicalBackend(self.device)
        for method in [
                backend.right_click, backend.left_click, backend.both_click, backend.finger_touch
        ]:
            self.assertIsNone(method())

    def test_click_methods_with_gui(self):
        for (method, expected_arg) in [(self.backend.right_click, NavInsID.RIGHT_CLICK),
                                       (self.backend.left_click, NavInsID.LEFT_CLICK),
                                       (self.backend.both_click, NavInsID.BOTH_CLICK)]:
            # mocking the underlying called method
            self.backend._ui.ask_for_click_action = MagicMock()

            self.assertIsNone(method())
            self.assertTrue(self.backend._ui.ask_for_click_action.called)
            self.assertEqual(self.backend._ui.ask_for_click_action.call_args, ((expected_arg, ), ))

    def test_finger_touch_with_gui(self):
        x, y = 3, 7
        # mocking the underlying called method
        self.backend._ui.ask_for_touch_action = MagicMock()

        self.assertIsNone(self.backend.finger_touch(x, y))
        self.assertTrue(self.backend._ui.ask_for_touch_action.called)
        self.assertEqual(self.backend._ui.ask_for_touch_action.call_args, ((x, y), ))

    def test_compare_methods_no_gui_bool(self):
        backend = StubPhysicalBackend(self.device)
        self.assertTrue(backend.compare_screen_with_snapshot(None))
        self.assertTrue(backend.compare_screen_with_text(None))

    def test_compare_screen_with_snapshot_with_gui(self):
        # mocking the underlying called method
        oracle = MagicMock()
        oracle.return_value = True
        self.backend._ui.check_screenshot = oracle

        path = "some/patch"
        self.assertIsNone(self.backend._last_valid_snap_path)
        self.assertTrue(self.backend.compare_screen_with_snapshot(path))
        self.assertTrue(oracle.called)
        self.assertEqual(self.backend._last_valid_snap_path, path)

        # comparing same snapshot, the underlying check function is not called
        oracle.reset_mock()
        self.assertTrue(self.backend.compare_screen_with_snapshot(path))
        self.assertFalse(oracle.called)
        self.assertEqual(self.backend._last_valid_snap_path, path)

    def test_compare_screen_with_snapshot_with_gui_error(self):
        # mocking the underlying called method
        oracle = MagicMock()
        oracle.return_value = False
        self.backend._ui.check_screenshot = oracle

        path = "some/patch"
        self.backend._last_valid_snap_path = None
        self.assertFalse(self.backend.compare_screen_with_snapshot(path))
        self.assertTrue(oracle.called)
        self.assertIsNone(self.backend._last_valid_snap_path)

    def test_compare_screen_with_text_with_gui_last_valid_snap_path_exists(self):
        path = "tests/snapshots/nanos/generic/00000.png"
        text = "Boilerplate"
        self.backend._last_valid_snap_path = path

        self.assertTrue(self.backend.compare_screen_with_text(text))
        self.assertFalse(self.backend.compare_screen_with_text("this text does not exist here"))

    def test_compare_screen_with_text_with_gui_last_valid_snap_path_does_not_exist(self):
        # mocking the underlying called method
        oracle = MagicMock()
        oracle.return_value = True
        self.backend._ui.check_text = oracle

        text = "sometext"
        self.assertTrue(self.backend.compare_screen_with_text(text))
        self.assertTrue(oracle.called)
        self.assertEqual(oracle.call_args, ((text, ), ))

    def test_wait_for_screen_change(self):
        self.assertIsNone(self.backend.wait_for_screen_change())

    def test_get_current_screen_content(self):
        self.assertListEqual(self.backend.get_current_screen_content(), list())
