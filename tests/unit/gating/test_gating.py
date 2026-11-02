from unittest import TestCase

from ragger.gating import GatingDescriptor, GatingSubCommand, GatingTxType
from ragger.tlv import LedgerStructType

ADDR = bytes.fromhex("6b175474e89094c44da98b954eedeac495271d0f")
SELECTOR = bytes.fromhex("70a08231")
SIGNATURE = bytes(range(70))

# TLV tags used in the assertions
STRUCT_TYPE = 0x01
VERSION = 0x02
DER_SIGNATURE = 0x15
ADDRESS = 0x22
CHAIN_ID = 0x23
SELECTOR_TAG = 0x40
INTRO_MSG = 0x82
TINY_URL = 0x83
TX_TYPE = 0x84


def parse_tlv(payload: bytes) -> list[tuple[int, bytes]]:
    """Parse a DER-tag/DER-length TLV payload into an ordered list of (tag, value)."""

    def read(buf, i):
        first = buf[i]
        i += 1
        if first < 0x80:
            return first, i
        size = first & 0x7F
        return int.from_bytes(buf[i : i + size], "big"), i + size

    fields = []
    i = 0
    while i < len(payload):
        tag, i = read(payload, i)
        length, i = read(payload, i)
        fields.append((tag, payload[i : i + length]))
        i += length
    return fields


class _Signer:
    def __init__(self) -> None:
        self.signed: bytes | None = None

    def sign(self, data: bytes) -> bytes:
        self.signed = data
        return SIGNATURE


class TestGatingDescriptor(TestCase):
    def test_serialize_all_fields(self):
        descriptor = GatingDescriptor(
            GatingTxType.TRANSACTION, ADDR, "Intro", "ledger.com/x", chain_id=1, selector=SELECTOR, signature=SIGNATURE
        )
        fields = parse_tlv(descriptor.serialize())
        self.assertEqual(
            [
                (STRUCT_TYPE, bytes([LedgerStructType.TYPE_GATED_SIGNING])),
                (VERSION, b"\x01"),
                (TX_TYPE, b"\x00"),
                (ADDRESS, ADDR),
                (CHAIN_ID, (1).to_bytes(8, "big")),
                (INTRO_MSG, b"Intro"),
                (TINY_URL, b"ledger.com/x"),
                (SELECTOR_TAG, SELECTOR),
                (DER_SIGNATURE, SIGNATURE),
            ],
            fields,
        )

    def test_optional_fields_omitted(self):
        descriptor = GatingDescriptor(GatingTxType.MESSAGE, ADDR, "Intro", "url", signature=SIGNATURE)
        tags = [tag for tag, _ in parse_tlv(descriptor.serialize())]
        self.assertNotIn(CHAIN_ID, tags)
        self.assertNotIn(SELECTOR_TAG, tags)
        self.assertEqual(DER_SIGNATURE, tags[-1])

    def test_signer_signs_every_field_but_the_signature(self):
        signer = _Signer()
        descriptor = GatingDescriptor(GatingTxType.TRANSACTION, ADDR, "Intro", "url", signer=signer)  # type: ignore[arg-type]
        payload = descriptor.serialize()
        self.assertIsNotNone(signer.signed)
        assert signer.signed is not None
        self.assertTrue(payload.startswith(signer.signed))
        self.assertEqual((DER_SIGNATURE, SIGNATURE), parse_tlv(payload)[-1])

    def test_explicit_signature_wins_over_signer(self):
        signer = _Signer()
        descriptor = GatingDescriptor(
            GatingTxType.TRANSACTION,
            ADDR,
            "Intro",
            "url",
            signer=signer,
            signature=b"\x00" * 70,  # type: ignore[arg-type]
        )
        self.assertEqual((DER_SIGNATURE, b"\x00" * 70), parse_tlv(descriptor.serialize())[-1])
        self.assertIsNone(signer.signed)

    def test_missing_signature_raises(self):
        with self.assertRaises(ValueError):
            GatingDescriptor(GatingTxType.TRANSACTION, ADDR, "Intro", "url").serialize()


class TestGatingChunks(TestCase):
    def test_single_chunk_layout(self):
        descriptor = GatingDescriptor(GatingTxType.TRANSACTION, ADDR, "Intro", "url", signature=SIGNATURE)
        payload = descriptor.serialize()
        apdus = descriptor.get_chunks()
        self.assertEqual(1, len(apdus))
        self.assertEqual(
            bytes([0xB0, 0x12, GatingSubCommand.SUB_CMD_PROVIDE_DESCRIPTOR, 0x00, len(payload) + 2])
            + len(payload).to_bytes(2, "big")
            + payload,
            apdus[0],
        )

    def test_multi_chunk_layout(self):
        descriptor = GatingDescriptor(
            GatingTxType.TRANSACTION, ADDR, "I" * 100, "u" * 30, chain_id=1, selector=bytes(32), signature=SIGNATURE
        )
        payload = descriptor.serialize()
        apdus = descriptor.get_chunks()
        self.assertGreater(len(apdus), 1)
        body = b""
        for index, apdu in enumerate(apdus):
            self.assertEqual(bytes([0xB0, 0x12, 0x01]), apdu[:3])
            self.assertEqual(0x00 if index == 0 else 0x80, apdu[3])
            self.assertEqual(len(apdu) - 5, apdu[4])
            body += apdu[5:]
        self.assertEqual(len(payload).to_bytes(2, "big") + payload, body)
