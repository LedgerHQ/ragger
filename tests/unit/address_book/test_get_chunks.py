from unittest import TestCase

from ragger.tlv import LedgerStructType
from ragger.address_book import AddressBookCommand, AddressBookSubCommand


class _Dummy(AddressBookCommand):
    """Minimal command exposing a fixed payload, to test the APDU framing alone."""
    subcommand = AddressBookSubCommand.SUB_CMD_REGISTER_IDENTITY
    struct_type = LedgerStructType.TYPE_REGISTER_IDENTITY

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def serialize(self) -> bytes:
        return self._payload


def reassemble(apdus, cla=0xB0, ins=0x10, p1=0x01):
    body = b""
    for index, apdu in enumerate(apdus):
        assert apdu[0] == cla and apdu[1] == ins and apdu[2] == p1
        assert apdu[3] == (0x00 if index == 0 else 0x80)
        lc = apdu[4]
        assert lc == len(apdu) - 5
        body += apdu[5:]
    return body


class TestGetChunksFraming(TestCase):

    def test_single_chunk_layout(self):
        apdus = _Dummy(b"\xaa\xbb").get_chunks()
        self.assertEqual(1, len(apdus))
        # CLA INS P1 P2 Lc | len-prefix(2) | payload
        self.assertEqual(bytes([0xB0, 0x10, 0x01, 0x00, 4]) + b"\x00\x02\xaa\xbb", apdus[0])

    def test_p1_is_the_subcommand(self):
        self.assertEqual(int(AddressBookSubCommand.SUB_CMD_REGISTER_IDENTITY),
                         _Dummy(b"x").get_chunks()[0][2])

    def test_length_prefix_is_two_bytes_big_endian(self):
        apdus = _Dummy(b"\x00" * 5).get_chunks()
        self.assertEqual(b"\x00\x05", apdus[0][5:7])

    def test_empty_payload_still_carries_prefix(self):
        apdus = _Dummy(b"").get_chunks()
        self.assertEqual(1, len(apdus))
        self.assertEqual(b"\x00\x00", apdus[0][5:7])

    def test_single_chunk_boundary(self):
        # prefix(2) + 253 == 255 -> exactly one full chunk
        apdus = _Dummy(b"\x01" * 253).get_chunks()
        self.assertEqual(1, len(apdus))
        self.assertEqual(255, apdus[0][4])

    def test_two_chunks_just_over_the_boundary(self):
        apdus = _Dummy(b"\x01" * 254).get_chunks()
        self.assertEqual(2, len(apdus))
        self.assertEqual(255, apdus[0][4])
        self.assertEqual(1, apdus[1][4])
        self.assertEqual(0x00, apdus[0][3])
        self.assertEqual(0x80, apdus[1][3])

    def test_multi_chunk_reassembles_to_prefixed_payload(self):
        payload = bytes(i % 256 for i in range(300))
        apdus = _Dummy(payload).get_chunks()
        self.assertEqual(2, len(apdus))  # 2 + 300 = 302 -> 255 + 47
        self.assertEqual([255, 47], [a[4] for a in apdus])
        self.assertEqual(len(payload).to_bytes(2, "big") + payload, reassemble(apdus))

    def test_cla_ins_override(self):
        apdus = _Dummy(b"x").get_chunks(cla=0xE0, ins=0x99)
        self.assertEqual(0xE0, apdus[0][0])
        self.assertEqual(0x99, apdus[0][1])
