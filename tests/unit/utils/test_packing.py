from unittest import TestCase

from ragger.utils import packing


class TestPacking(TestCase):

    def test_pack_APDU(self):
        cla, ins, p1, p2, data = 1, 2, 3, 4, b"data"
        expected = bytes.fromhex("0102030404") + data
        self.assertEqual(expected, packing.pack_APDU(cla, ins, p1, p2, data))
        expected = bytes.fromhex("0102030400")
        self.assertEqual(expected, packing.pack_APDU(cla, ins, p1, p2))
        expected = bytes.fromhex("0102030004") + data
        self.assertEqual(expected, packing.pack_APDU(cla, ins, p1, data=data))
        expected = bytes.fromhex("0102000404") + data
        self.assertEqual(expected, packing.pack_APDU(cla, ins, p2=p2, data=data))
        expected = bytes.fromhex("0102000000")
        self.assertEqual(expected, packing.pack_APDU(cla, ins))
