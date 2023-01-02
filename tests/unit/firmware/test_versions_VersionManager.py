from unittest import TestCase

from semver import VersionInfo

from ragger.firmware.versions import VersionManager


class FakeVersionManager(VersionManager):
    V100 = VersionInfo(1, 0, 0)
    V123 = VersionInfo(1, 2, 3)
    V125 = VersionInfo(1, 2, 5)
    V134 = VersionInfo(1, 3, 4)
    V160 = VersionInfo(1, 6, 0)
    V900 = VersionInfo(9, 0, 0)


class TestVersionManager(TestCase):

    def test_get_last(self):
        self.assertEqual(FakeVersionManager.get_last(), FakeVersionManager.V900.value)

    def test_get_last_errors(self):
        with self.assertRaises(ValueError):
            FakeVersionManager.get_last(minor=1)
        with self.assertRaises(ValueError):
            FakeVersionManager.get_last(patch=1)
        with self.assertRaises(ValueError):
            FakeVersionManager.get_last(minor=1, patch=1)

    def test_get_last_major(self):
        self.assertEqual(FakeVersionManager.get_last(major=1), FakeVersionManager.V160.value)

    def test_get_last_major_minor(self):
        self.assertEqual(FakeVersionManager.get_last(major=1, minor=2),
                         FakeVersionManager.V125.value)

    def test_get_last_major_minor_patch(self):
        self.assertEqual(FakeVersionManager.get_last(major=1, minor=2, patch=3),
                         FakeVersionManager.V123.value)

    def test_get_last_major_minor_patch_error_does_not_exist(self):
        with self.assertRaises(ValueError):
            FakeVersionManager.get_last(major=12, minor=13, patch=14)

    def test_get_last_from_string_major_minor(self):
        self.assertEqual(FakeVersionManager.get_last_from_string("1.2"),
                         FakeVersionManager.V125.value)

    def test_get_last_from_string_major_minor_patch(self):
        self.assertEqual(FakeVersionManager.get_last_from_string("1.2.3"),
                         FakeVersionManager.V123.value)
