from unittest import TestCase

from ragger.backend import BackendInterface
from ragger.backend.stub import StubBackend
from ragger.utils.structs import RAPDU


class TestStubBackend(TestCase):

    def setUp(self):
        self.stub = StubBackend(None)

    def test_can_instantiate(self):
        self.assertIsInstance(self.stub, BackendInterface)

    def test_emtpy_methods(self):
        for func in (self.stub.handle_usb_reset, self.stub.send_raw, self.stub.right_click,
                     self.stub.left_click, self.stub.both_click, self.stub.finger_touch,
                     self.stub.wait_for_screen_change, self.stub.get_current_screen_content,
                     self.stub.pause_ticker, self.stub.resume_ticker, self.stub.send_tick):
            self.assertIsNone(func())
        for func in (self.stub.receive, self.stub.exchange_raw):
            self.assertEqual(func(), RAPDU(0x9000, b""))
        for func in (self.stub.compare_screen_with_snapshot, self.stub.compare_screen_with_text):
            self.assertTrue(func(None))
