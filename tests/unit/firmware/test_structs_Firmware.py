from unittest import TestCase

from semver import VersionInfo

from ragger.firmware import Firmware, SDK_VERSIONS


class TestFirmware(TestCase):

    def test_firmware_fetch_all(self):
        for name, versions in SDK_VERSIONS.items():
            for version in versions:
                Firmware(name, str(version.value))

    def test_firmware_incomplete_version(self):
        name = "nanosp"
        version = "1.0"
        firmware = Firmware(name, version)
        self.assertEqual(firmware.device, name)
        self.assertEqual(firmware.version, version)
        # WARNING: this may need to be updated if a new firmware *patch* version is released on NanoS+ (1.0.5)
        self.assertEqual(firmware.semantic_version, VersionInfo(1, 0, 4))

    def test_firmware_not_existing_version(self):
        with self.assertRaises(KeyError):
            Firmware("non existing device", "not important")

    def test_has_bagl(self):
        self.assertTrue(Firmware("nanosp", "1.0").has_bagl)
        self.assertFalse(Firmware("stax", "1.0").has_bagl)

    def test_has_nbgl(self):
        self.assertFalse(Firmware("nanosp", "1.0").has_nbgl)
        self.assertTrue(Firmware("stax", "1.0").has_nbgl)
