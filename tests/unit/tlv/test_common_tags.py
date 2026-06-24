from unittest import TestCase

from ragger.tlv import LedgerCommonFieldTag


class TestCommonFieldTag(TestCase):

    def test_known_values(self):
        self.assertEqual(0x01, LedgerCommonFieldTag.STRUCTURE_TYPE)
        self.assertEqual(0x02, LedgerCommonFieldTag.VERSION)
        self.assertEqual(0x12, LedgerCommonFieldTag.CHALLENGE)
        self.assertEqual(0x15, LedgerCommonFieldTag.DER_SIGNATURE)
        self.assertEqual(0x21, LedgerCommonFieldTag.COIN_TYPE)
        self.assertEqual(0x23, LedgerCommonFieldTag.CHAIN_ID)
        self.assertEqual(0x29, LedgerCommonFieldTag.HMAC_PROOF)
        self.assertEqual(0x35, LedgerCommonFieldTag.TARGET_DEVICE)

    def test_values_are_unique(self):
        values = [int(tag) for tag in LedgerCommonFieldTag]
        self.assertEqual(len(values), len(set(values)))

    def test_covers_envelope_and_certificate_ranges(self):
        # §3.2.1-3.2.4: structure (0x01-0x02), envelope (0x10-0x16),
        # common content (0x20-0x29), certificate (0x30-0x36)
        present = {int(tag) for tag in LedgerCommonFieldTag}
        for value in list(range(0x10, 0x17)) + list(range(0x20, 0x2a)) + list(range(0x30, 0x37)):
            self.assertIn(value, present, f"missing common tag {value:#04x}")
