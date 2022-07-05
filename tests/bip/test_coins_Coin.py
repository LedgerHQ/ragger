from unittest import TestCase

from ragger.bip.coins import Coin, Bitcoin


class TestCoin(TestCase):

    def test_from_type_ok(self):
        self.assertEqual(Coin.from_type(0x00), Bitcoin)

    def test_from_type_error_unknown(self):
        with self.assertRaises(ValueError) as error:
            Coin.from_type(0xff)
        self.assertIn("Coin", str(error.exception))
