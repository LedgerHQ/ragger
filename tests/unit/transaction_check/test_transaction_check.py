from typing import Any
from unittest import TestCase

from ragger.tlv import LedgerCommonFieldTag, LedgerStructType, TxSimulationFieldTag, format_tlv
from ragger.transaction_check import (
    TRANSACTION_CHECK_CLA,
    TRANSACTION_CHECK_INS,
    SimulationType,
    TransactionCheck,
    TransactionCheckCategory,
    TransactionCheckRisk,
    TransactionCheckSubCommand,
    get_opt_in_apdu,
)

TX_HASH = b"\xab" * 32
DOMAIN_HASH = b"\xcd" * 32
SIGNATURE = b"\x30\x02\x01\x01"


class FakePartner:
    """Signing partner recording the signed data."""

    def __init__(self, signature: bytes = SIGNATURE) -> None:
        self.signature = signature
        self.signed: list[bytes] = []

    def sign(self, data: bytes) -> bytes:
        self.signed.append(data)
        return self.signature


def make(**kwargs) -> TransactionCheck:
    params: dict[str, Any] = {
        "address": b"\x11" * 20,
        "tx_hash": TX_HASH,
        "risk": TransactionCheckRisk.WARNING,
        "category": TransactionCheckCategory.DAPP,
        "tiny_url": "https://ledger.com/r/1",
        "partner": FakePartner(),
    }
    params.update(kwargs)
    return TransactionCheck(**params)


def reassemble(apdus: list[bytes]) -> bytes:
    body = b""
    for index, apdu in enumerate(apdus):
        assert apdu[0] == TRANSACTION_CHECK_CLA and apdu[1] == TRANSACTION_CHECK_INS
        assert apdu[2] == TransactionCheckSubCommand.SUB_CMD_DESCRIPTOR
        assert apdu[3] == (0x00 if index == 0 else 0x80)
        assert apdu[4] == len(apdu) - 5
        body += apdu[5:]
    return body


class TestSerialize(TestCase):
    def test_mandatory_fields(self):
        expected = format_tlv(LedgerCommonFieldTag.STRUCTURE_TYPE, LedgerStructType.TYPE_TX_SIMULATION)
        expected += format_tlv(LedgerCommonFieldTag.VERSION, 1)
        expected += format_tlv(TxSimulationFieldTag.SIMULATION_TYPE, SimulationType.TRANSACTION)
        expected += format_tlv(LedgerCommonFieldTag.ADDRESS, b"\x11" * 20)
        expected += format_tlv(LedgerCommonFieldTag.TX_HASH, TX_HASH)
        expected += format_tlv(TxSimulationFieldTag.NORMALIZED_RISK, TransactionCheckRisk.WARNING)
        expected += format_tlv(TxSimulationFieldTag.NORMALIZED_CATEGORY, TransactionCheckCategory.DAPP)
        expected += format_tlv(TxSimulationFieldTag.TINY_URL, "https://ledger.com/r/1")
        expected += format_tlv(LedgerCommonFieldTag.DER_SIGNATURE, SIGNATURE)
        self.assertEqual(expected, make().serialize())

    def test_optional_fields(self):
        payload = make(
            simulation_type=SimulationType.TYPED_MESSAGE,
            chain_id=1,
            domain_hash=DOMAIN_HASH,
            provider_message="Scam",
        ).serialize()
        self.assertIn(format_tlv(LedgerCommonFieldTag.CHAIN_ID, (1).to_bytes(8, "big")), payload)
        self.assertIn(format_tlv(LedgerCommonFieldTag.DOMAIN_HASH, DOMAIN_HASH), payload)
        self.assertIn(format_tlv(TxSimulationFieldTag.PROVIDER_MESSAGE, "Scam"), payload)
        self.assertIn(format_tlv(TxSimulationFieldTag.SIMULATION_TYPE, SimulationType.TYPED_MESSAGE), payload)

    def test_chain_id_zero_is_sent(self):
        payload = make(chain_id=0).serialize()
        self.assertIn(format_tlv(LedgerCommonFieldTag.CHAIN_ID, bytes(8)), payload)

    def test_text_address_is_encoded(self):
        payload = make(address="9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM").serialize()
        self.assertIn(format_tlv(LedgerCommonFieldTag.ADDRESS, b"9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"), payload)

    def test_signature_covers_every_other_tlv(self):
        partner = FakePartner()
        payload = make(partner=partner, chain_id=1).serialize()
        self.assertEqual(payload, partner.signed[0] + format_tlv(LedgerCommonFieldTag.DER_SIGNATURE, SIGNATURE))

    def test_explicit_signature(self):
        partner = FakePartner()
        payload = make(partner=None, signature=b"\x30\x01\x00").serialize()
        self.assertTrue(payload.endswith(format_tlv(LedgerCommonFieldTag.DER_SIGNATURE, b"\x30\x01\x00")))
        self.assertEqual([], partner.signed)

    def test_partner_or_signature_required(self):
        with self.assertRaises(ValueError):
            make(partner=None)

    def test_hash_lengths_are_checked(self):
        with self.assertRaises(ValueError):
            make(tx_hash=b"\x00" * 31)
        with self.assertRaises(ValueError):
            make(domain_hash=b"\x00" * 33)


class TestApdus(TestCase):
    def test_single_chunk(self):
        check = make()
        apdus = check.get_chunks()
        self.assertEqual(1, len(apdus))
        payload = check.serialize()
        self.assertEqual(len(payload).to_bytes(2, "big") + payload, reassemble(apdus))

    def test_two_chunks(self):
        check = make(chain_id=1, domain_hash=DOMAIN_HASH, provider_message="A" * 25, tiny_url="B" * 30)
        check.address = b"C" * 44
        check.partner = FakePartner(b"\x30" * 72)
        apdus = check.get_chunks()
        self.assertEqual(2, len(apdus))
        self.assertEqual(0xFF, apdus[0][4])
        payload = check.serialize()
        self.assertEqual(len(payload).to_bytes(2, "big") + payload, reassemble(apdus))

    def test_opt_in(self):
        self.assertEqual(bytes([0xB0, 0x11, 0x01, 0x00, 0x00]), get_opt_in_apdu())
