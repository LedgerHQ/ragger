from unittest import TestCase

from ragger.bip import pack_derivation_path

MAX_VALUE = 2**31 - 1

HARDENED_INDEX = 2**31


class TestPath(TestCase):

    def _test_level_n(self, n: int):
        for variant in [0, 255, 81845, 887587, MAX_VALUE]:
            for hardening in [False, True]:
                hardening_char = '\'' if hardening else ''
                previous_levels = "0/" * (n - 1)
                path = f'm/{previous_levels}{variant}{hardening_char}'
                packed = pack_derivation_path(path)
                self.assertEqual(packed[0], n)
                self.assertEqual(len(packed), 1 + n * 4)
                last_value = int.from_bytes(packed[len(packed) - 4:len(packed)], byteorder="big")
                self.assertEqual(last_value, variant | (HARDENED_INDEX if hardening else 0))

    def test_errors(self):
        with self.assertRaises(ValueError) as e:
            pack_derivation_path("")
        with self.assertRaises(ValueError) as e:
            pack_derivation_path("m/0/")
        with self.assertRaises(ValueError) as e:
            pack_derivation_path("m//0")
        with self.assertRaises(ValueError) as e:
            pack_derivation_path("m/a")

    def test_level_path_0(self):
        packed = pack_derivation_path("m")
        self.assertEqual(packed[0], 0)
        self.assertEqual(len(packed), 1)

    def test_level_path_1(self):
        self._test_level_n(1)

    def test_level_path_2(self):
        self._test_level_n(2)

    def test_level_path_3(self):
        self._test_level_n(3)

    def test_level_path_4(self):
        self._test_level_n(4)

    def test_level_path_5(self):
        self._test_level_n(5)

    def test_level_path_6(self):
        self._test_level_n(6)

    def test_level_path_7(self):
        self._test_level_n(7)

    def test_level_path_8(self):
        self._test_level_n(8)

    def test_level_path_9(self):
        self._test_level_n(9)

    def test_level_path_10(self):
        self._test_level_n(10)
