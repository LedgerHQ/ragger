from unittest import TestCase

from ragger.utils.structs import RAPDU


class TestRAPDU(TestCase):

    def test_raw(self):
        status = 0x9000
        data = bytes.fromhex('0123456789abcdef')
        expected = data + bytes.fromhex('9000')
        self.assertEqual(RAPDU(status, data).raw, expected)
