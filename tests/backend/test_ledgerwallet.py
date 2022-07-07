from typing import Optional
from unittest import TestCase
from unittest.mock import patch, MagicMock

from ragger import Firmware, RAPDU, ExceptionRAPDU
from ragger.backend import LedgerWalletBackend
from ragger.backend.interface import RaisePolicy


class TestLedgerWalletBackend(TestCase):

    def setUp(self):
        self.device = MagicMock()
        self.firmware = Firmware("nanos", "2.1")
        self.backend = LedgerWalletBackend(self.firmware)

    def check_rapdu(self, rapdu: RAPDU, status: int = 0x9000, payload: Optional[bytes] = None):
        self.assertIsInstance(rapdu, RAPDU)
        self.assertEqual(rapdu.status, status)
        self.assertEqual(rapdu.data, payload)

    def test_contextmanager(self):
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [MagicMock()]
            self.assertIsNone(self.backend._client)
            with self.backend as backend:
                self.assertEqual(self.backend, backend)
        self.assertIsNotNone(self.backend._client)

    def test_send_raw(self):
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [MagicMock()]
            with self.backend:
                self.assertIsNone(self.backend.send_raw(b""))

    def test_receive_ok(self):
        status, payload = 0x9000, b"something"
        self.device.read.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                rapdu = self.backend.receive()
        self.check_rapdu(rapdu, payload=payload)

    def test_receive_ok_raise(self):
        status, payload = 0x8000, b"something"
        self.device.read.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                self.backend.set_raise_policy(RaisePolicy.RAISE_ALL)
                with self.assertRaises(ExceptionRAPDU) as error:
                    self.backend.receive()
        self.assertEqual(error.exception.status, status)

    def test_receive_nok_no_raise(self):
        status, payload = 0x8000, b"something"
        self.device.read.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                self.backend.set_raise_policy(RaisePolicy.RAISE_NOTHING)
                rapdu = self.backend.receive()
        self.check_rapdu(rapdu, status=status, payload=payload)

    def test_receive_nok_raise(self):
        status, payload = 0x8000, b"something"
        self.device.read.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                with self.assertRaises(ExceptionRAPDU) as error:
                    self.backend.receive()
        self.assertEqual(error.exception.status, status)

    def test_exchange_raw_ok(self):
        status, payload = 0x9000, b"something"
        self.device.exchange.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                rapdu = self.backend.exchange_raw(b"")
        self.check_rapdu(rapdu, payload=payload)

    def test_exchange_raw_nok_no_raise(self):
        status, payload = 0x8000, b"something"
        self.device.exchange.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                self.backend.set_raise_policy(RaisePolicy.RAISE_NOTHING)
                rapdu = self.backend.exchange_raw(b"")
        self.check_rapdu(rapdu, status=status, payload=payload)

    def test_exchange_raw_nok_raise(self):
        status, payload = 0x8000, b"something"
        self.device.exchange.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                with self.assertRaises(ExceptionRAPDU) as error:
                    self.backend.exchange_raw(b"")
        self.assertEqual(error.exception.status, status)

    def test_exchange_async_raw_ok(self):
        status, payload = 0x9000, b"something"
        self.device.read.return_value = payload + bytes.fromhex(f"{status:x}")
        with patch("ledgerwallet.client.enumerate_devices") as devices:
            devices.return_value = [self.device]
            with self.backend:
                self.assertIsNone(self.backend.last_async_response)
                with self.backend.exchange_async_raw(b""):
                    self.backend.right_click()
                    self.backend.left_click()
                    self.backend.both_click()
        self.check_rapdu(self.backend.last_async_response, payload=payload)
