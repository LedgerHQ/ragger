from ledgered.devices import DeviceType, Devices
from unittest import TestCase
from unittest.mock import patch

from ragger.error import ExceptionRAPDU
from ragger.utils import RAPDU
from ragger.backend import LedgerCommBackend
from ragger.backend import RaisePolicy


class TestLedgerCommbackend(TestCase):
    """
    Test patterns explained:

    ```
    def test_something(self):
        # patches the HID transport layer used in LedgerComm to communicate with the USB
        with patch("ledgercomm.transport.HID") as mock:
            # saving the mock somewhere to check .open .send .recv methods
            self.hid = mock
            # starts the backend
            with self.backend:
    ```
    """

    def setUp(self):
        self.device = Devices.get_by_type(DeviceType.NANOS)
        self.backend = LedgerCommBackend(self.device)

    def check_rapdu(self, rapdu: RAPDU, status: int = 0x9000, payload: bytes = None):
        self.assertIsInstance(rapdu, RAPDU)
        self.assertEqual(rapdu.status, status)
        self.assertEqual(rapdu.data, payload)

    def test_contextmanager(self):
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            with self.backend:
                self.assertTrue(self.hid.called)
                self.assertTrue(self.hid().open.called)
                self.assertFalse(self.hid().close.called)
        self.assertTrue(self.hid().close.called)
        self.assertEqual(self.backend._client.com, self.hid())

    def test_send_raw(self):
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            with self.backend:
                self.assertFalse(self.hid().send.called)
                self.backend.send_raw(bytes.fromhex("00000000"))
        self.assertTrue(self.hid().send.called)

    def test_receive_ok(self):
        success, payload = 0x9000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().recv.return_value = (success, payload)
            with self.backend:
                rapdu = self.backend.receive()
        self.check_rapdu(rapdu, payload=payload)

    def test_receive_ok_raises(self):
        failure, payload = 0x9000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().recv.return_value = (failure, payload)
            with self.backend:
                self.backend.raise_policy = RaisePolicy.RAISE_ALL
                with self.assertRaises(ExceptionRAPDU) as error:
                    self.backend.receive()
        self.assertEqual(error.exception.status, failure)

    def test_receive_nok(self):
        failure, payload = 0x8000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().recv.return_value = (failure, payload)
            with self.backend:
                self.backend.raise_policy = RaisePolicy.RAISE_NOTHING
                rapdu = self.backend.receive()
        self.check_rapdu(rapdu, status=failure, payload=payload)

    def test_receive_nok_raises(self):
        failure, payload = 0x8000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().recv.return_value = (failure, payload)
            with self.backend:
                with self.assertRaises(ExceptionRAPDU) as error:
                    self.backend.receive()
        self.assertEqual(error.exception.status, failure)

    def test_exchange_raw(self):
        success, payload = 0x9000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().exchange.return_value = (success, payload)
            with self.backend:
                self.assertFalse(self.hid().exchange.called)
                rapdu = self.backend.exchange_raw(b"")
        self.assertTrue(self.hid().exchange.called)
        self.check_rapdu(rapdu, payload=payload)

    def test_exchange_raw_raises(self):
        failure, payload = 0x8000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().exchange.return_value = (failure, payload)
            with self.backend:
                with self.assertRaises(ExceptionRAPDU):
                    self.backend.exchange_raw(b"")

    def test_exchange_async_raw(self):
        success, payload = 0x9000, b"something"
        with patch("ledgercomm.transport.HID") as mock:
            self.hid = mock
            self.hid().recv.return_value = (success, payload)
            with self.backend:
                self.assertIsNone(self.backend.last_async_response)
                with self.backend.exchange_async_raw(b""):
                    self.backend.right_click()
                    self.backend.left_click()
                    self.backend.both_click()
        self.assertIsNotNone(self.backend.last_async_response)
        self.check_rapdu(self.backend.last_async_response, payload=payload)
