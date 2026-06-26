from unittest import TestCase

from ragger.tlv import BlockchainFamily, LedgerStructType
from ragger.address_book import (
    RegisterIdentity,
    EditContactName,
    EditIdentifier,
    EditScope,
    RegisterLedgerAccount,
    EditLedgerAccount,
    ProvideContact,
    ProvideLedgerAccountContact,
)

FAMILY = BlockchainFamily.ETHEREUM
ADDR = bytes.fromhex("6b175474e89094c44da98b954eedeac495271d0f")  # 20 bytes
PATH = "m/44'/60'/0'/0/0"
GH = bytes(range(64))  # 64-byte group handle
PR = bytes(range(32))  # 32-byte hmac proof
REST = bytes(range(32, 64))  # 32-byte hmac rest

# TLV tags used in the assertions
STRUCT_TYPE = 0x01
VERSION = 0x02
DERIVATION_PATH = 0x69
CHAIN_ID = 0x23
HMAC_PROOF = 0x29
BLOCKCHAIN_FAMILY = 0x51
CONTACT_NAME = 0xf0
SCOPE = 0xf1
ACCOUNT_IDENTIFIER = 0xf2
GROUP_HANDLE = 0xf6
HMAC_REST = 0xf7


def parse_tlv(payload: bytes) -> dict:
    """Parse a DER-tag/DER-length TLV payload into a {tag: value} dict."""

    def read(buf, i):
        first = buf[i]
        i += 1
        if first & 0x80:
            n = first & 0x7f
            return int.from_bytes(buf[i:i + n], "big"), i + n
        return first, i

    out = {}
    i = 0
    while i < len(payload):
        tag, i = read(payload, i)
        length, i = read(payload, i)
        out[tag] = payload[i:i + length]
        i += length
    return out


class TestRegisterIdentity(TestCase):

    def test_serialized_fields(self):
        cmd = RegisterIdentity(identifier=ADDR,
                               contact_name="Alice",
                               scope="Eth Address 1",
                               derivation_path=PATH,
                               chain_id=1,
                               blockchain_family=BlockchainFamily.ETHEREUM)
        tlv = parse_tlv(cmd.serialize())
        self.assertEqual(bytes([LedgerStructType.TYPE_REGISTER_IDENTITY]), tlv[STRUCT_TYPE])
        self.assertEqual(b"\x01", tlv[VERSION])
        self.assertEqual(b"Alice", tlv[CONTACT_NAME])
        self.assertEqual(b"Eth Address 1", tlv[SCOPE])
        self.assertEqual(ADDR, tlv[ACCOUNT_IDENTIFIER])
        self.assertEqual(b"\x01", tlv[CHAIN_ID])
        self.assertEqual(bytes([BlockchainFamily.ETHEREUM]), tlv[BLOCKCHAIN_FAMILY])
        self.assertNotIn(GROUP_HANDLE, tlv)
        self.assertNotIn(HMAC_PROOF, tlv)

    def test_group_handle_and_proof_emitted_together(self):
        cmd = RegisterIdentity(identifier=ADDR,
                               contact_name="Alice",
                               scope="S",
                               derivation_path=PATH,
                               chain_id=1,
                               blockchain_family=FAMILY,
                               group_handle=GH,
                               hmac_proof=PR)
        tlv = parse_tlv(cmd.serialize())
        self.assertEqual(GH, tlv[GROUP_HANDLE])
        self.assertEqual(PR, tlv[HMAC_PROOF])

    def test_group_handle_without_proof_raises(self):
        cmd = RegisterIdentity(identifier=ADDR,
                               contact_name="Alice",
                               scope="S",
                               derivation_path=PATH,
                               chain_id=1,
                               blockchain_family=FAMILY,
                               group_handle=GH)
        with self.assertRaises(AssertionError):
            cmd.serialize()

    def test_contact_name_too_long_raises(self):
        cmd = RegisterIdentity(identifier=ADDR,
                               contact_name="A" * 33,
                               scope="S",
                               derivation_path=PATH,
                               chain_id=1,
                               blockchain_family=FAMILY)
        with self.assertRaises(AssertionError):
            cmd.serialize()


class TestBlockchainFamily(TestCase):

    def test_ethereum_includes_chain_id(self):
        cmd = RegisterIdentity(identifier=ADDR,
                               contact_name="A",
                               scope="S",
                               derivation_path=PATH,
                               chain_id=42,
                               blockchain_family=FAMILY)
        tlv = parse_tlv(cmd.serialize())
        self.assertIn(CHAIN_ID, tlv)
        self.assertEqual(b"\x2a", tlv[CHAIN_ID])

    def test_non_ethereum_omits_chain_id(self):
        # When chain_id is explicitly None (not passed), it should not be serialized
        cmd = RegisterIdentity(identifier=ADDR,
                               contact_name="A",
                               scope="S",
                               derivation_path=PATH,
                               blockchain_family=BlockchainFamily.BITCOIN)
        tlv = parse_tlv(cmd.serialize())
        self.assertNotIn(CHAIN_ID, tlv)
        self.assertEqual(bytes([BlockchainFamily.BITCOIN]), tlv[BLOCKCHAIN_FAMILY])


class TestValidations(TestCase):

    def test_bad_group_handle_length(self):
        cmd = EditContactName(old_contact_name="old",
                              new_contact_name="new",
                              hmac_proof=PR,
                              group_handle=b"\x00" * 10,
                              derivation_path=PATH)
        with self.assertRaises(AssertionError):
            cmd.serialize()

    def test_bad_hmac_proof_length(self):
        cmd = EditContactName(old_contact_name="old",
                              new_contact_name="new",
                              hmac_proof=b"\x00" * 10,
                              group_handle=GH,
                              derivation_path=PATH)
        with self.assertRaises(AssertionError):
            cmd.serialize()


class TestSubCommandMapping(TestCase):

    def _cases(self):
        return [
            (RegisterIdentity(ADDR, "A", "S", PATH, FAMILY, 1), 0x01, 0x2d),
            (EditContactName("o", "n", PR, GH, PATH), 0x02, 0x2e),
            (EditIdentifier(ADDR, ADDR, "A", "S", PATH, PR, REST, GH, FAMILY, 1), 0x03, 0x31),
            (EditScope("o", "n", ADDR, "A", PATH, PR, REST, GH, FAMILY, 1), 0x04, 0x32),
            (RegisterLedgerAccount("A", PATH, FAMILY, 1), 0x11, 0x2f),
            (EditLedgerAccount("o", "n", PATH, PR, FAMILY, 1), 0x12, 0x30),
            (ProvideContact(ADDR, GH, PR, REST, "A", "S", PATH, FAMILY, 1), 0x20, 0x33),
            (ProvideLedgerAccountContact(PR, "A", PATH, FAMILY, 1), 0x21, 0x34),
        ]

    def test_subcommand_struct_type_and_p1(self):
        for cmd, p1, struct_type in self._cases():
            with self.subTest(cmd=type(cmd).__name__):
                self.assertEqual(p1, int(cmd.subcommand))
                self.assertEqual(p1, cmd.get_chunks()[0][2])
                tlv = parse_tlv(cmd.serialize())
                self.assertEqual(bytes([struct_type]), tlv[STRUCT_TYPE])


class TestEditAndProvideContent(TestCase):

    def test_edit_identifier_carries_old_and_new_address(self):
        new_addr = bytes(range(20))
        cmd = EditIdentifier(ADDR, new_addr, "A", "S", PATH, PR, REST, GH, FAMILY, 1)
        tlv = parse_tlv(cmd.serialize())
        self.assertEqual(new_addr, tlv[ACCOUNT_IDENTIFIER])
        self.assertEqual(ADDR, tlv[0xf4])  # PREVIOUS_IDENTIFIER
        self.assertEqual(PR, tlv[HMAC_PROOF])
        self.assertEqual(REST, tlv[HMAC_REST])

    def test_provide_ledger_account_contact_has_no_address_or_handle(self):
        cmd = ProvideLedgerAccountContact(PR, "ETH main", PATH, FAMILY, 1)
        tlv = parse_tlv(cmd.serialize())
        self.assertEqual(PR, tlv[HMAC_PROOF])
        self.assertNotIn(ACCOUNT_IDENTIFIER, tlv)
        self.assertNotIn(GROUP_HANDLE, tlv)
        self.assertNotIn(HMAC_REST, tlv)
