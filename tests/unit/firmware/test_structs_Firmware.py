from unittest import TestCase

from ragger.firmware import Firmware


class TestFirmware(TestCase):

    def test_firmware_not_existing_version(self):
        with self.assertRaises(ValueError):
            Firmware(10)

    def test_is_nano(self):
        self.assertTrue(Firmware.NANOSP.is_nano)
        self.assertFalse(Firmware.STAX.is_nano)

    def test_has_bagl(self):
        self.assertTrue(Firmware.NANOSP.has_bagl)
        self.assertFalse(Firmware.STAX.has_bagl)

    def test_has_nbgl(self):
        self.assertFalse(Firmware.NANOSP.has_nbgl)
        self.assertTrue(Firmware.STAX.has_nbgl)
