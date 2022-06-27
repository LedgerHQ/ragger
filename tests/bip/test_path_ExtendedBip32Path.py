from unittest import TestCase

from ragger.bip.path import ExtendedBip32Path
from ragger.bip.utils import BIP


class TestExtendedBip32Path(TestCase):

    def test_error_empty(self):
        with self.assertRaises(ValueError):
            ExtendedBip32Path()
        with self.assertRaises(ValueError):
            ExtendedBip32Path(b'')

    def test_one_level_path(self):

        for purpose in BIP:
            for hardening in ["00", "80"]:
                path = ExtendedBip32Path(bytes.fromhex(f"{hardening}0000{purpose:x}"))
                self.assertEqual(path.purpose, purpose)
                with self.assertRaises(IndexError):
                    path.coin_type
                with self.assertRaises(IndexError):
                    path.account
                with self.assertRaises(IndexError):
                    path.change
                with self.assertRaises(IndexError):
                    path.address_index

    def test_two_level_path(self):
        purpose = BIP.BIP44
        coin_type = 0x77
        for hardening in ["00", "80"]:
            path = ExtendedBip32Path(bytes.fromhex(f"{hardening}0000{purpose:x}" \
                                                   f"{hardening}0000{coin_type:x}"))
            self.assertEqual(path.purpose, purpose)
            self.assertEqual(path.coin_type, coin_type)
            with self.assertRaises(IndexError):
                path.account
            with self.assertRaises(IndexError):
                path.change
            with self.assertRaises(IndexError):
                path.address_index

    def test_three_level_path(self):
        purpose = BIP.BIP49
        coin_type = 0xf3
        account = 0x2e
        for hardening in ["00", "80"]:
            path = ExtendedBip32Path(bytes.fromhex(f"{hardening}0000{purpose:x}" \
                                                   f"{hardening}0000{coin_type:x}" \
                                                   f"{hardening}0000{account:x}"))
            self.assertEqual(path.purpose, purpose)
            self.assertEqual(path.coin_type, coin_type)
            self.assertEqual(path.account, account)
            with self.assertRaises(IndexError):
                path.change
            with self.assertRaises(IndexError):
                path.address_index

    def test_four_level_path(self):
        purpose = BIP.BIP84
        coin_type = 0xab
        account = 0xcc
        change = 0x23
        for hardening in ["00", "80"]:
            path = ExtendedBip32Path(bytes.fromhex(f"{hardening}0000{purpose:x}" \
                                                   f"{hardening}0000{coin_type:x}" \
                                                   f"{hardening}0000{account:x}" \
                                                   f"000000{change:x}"))
            self.assertEqual(path.purpose, purpose)
            self.assertEqual(path.coin_type, coin_type)
            self.assertEqual(path.account, account)
            self.assertEqual(path.change, change)
            with self.assertRaises(IndexError):
                path.address_index

    def test_five_level_path(self):
        purpose = BIP.BIP86
        coin_type = 0xc0
        account = 0x5e
        change = 0x99
        index = 0x45
        for hardening in ["00", "80"]:
            path = ExtendedBip32Path(bytes.fromhex(f"{hardening}0000{purpose:x}" \
                                                   f"{hardening}0000{coin_type:x}" \
                                                   f"{hardening}0000{account:x}" \
                                                   f"000000{change:x}" \
                                                   f"000000{index:x}"))
            self.assertEqual(path.purpose, purpose)
            self.assertEqual(path.coin_type, coin_type)
            self.assertEqual(path.account, account)
            self.assertEqual(path.change, change)
            self.assertEqual(path.address_index, index)

    def test_change_error_no_hardening(self):
        change = 0x23
        path = ExtendedBip32Path(bytes.fromhex(f"80000000" \
                                               f"80000000" \
                                               f"80000000" \
                                               f"800000{change:x}"))
        self.assertNotEqual(path.change, change)
        self.assertEqual(path.change, change | 0x80000000)

    def test_address_index_error_no_hardening(self):
        index = 0x45
        path = ExtendedBip32Path(bytes.fromhex(f"80000000" \
                                               f"80000000" \
                                               f"80000000" \
                                               f"00000000" \
                                               f"800000{index:x}"))
        self.assertNotEqual(path.address_index, index)
        self.assertEqual(path.address_index, index | 0x80000000)
