from unittest import TestCase

from ragger.firmware import Firmware


class TestFirmware(TestCase):

    def test_firmware_not_existing_version(self):
        with self.assertRaises(ValueError):
            Firmware(10)

    def test_is_nano(self):
        self.assertTrue(Firmware.NANOSP.is_nano)
        self.assertFalse(Firmware.STAX.is_nano)
