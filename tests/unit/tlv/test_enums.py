from unittest import TestCase

from ragger.tlv import (
    LedgerStructType,
    BlockchainFamily,
    TrustedNameType,
    TrustedNameSource,
    SimulationType,
    ProxyDelegatorType,
    LesMultisigRole,
    LkrpStepType,
)


class TestStructType(TestCase):
    def test_known_values(self):
        self.assertEqual(0x01, LedgerStructType.TYPE_CERTIFICATE)
        self.assertEqual(0x2D, LedgerStructType.TYPE_REGISTER_IDENTITY)
        self.assertEqual(0x33, LedgerStructType.TYPE_PROVIDE_CONTACT)
        self.assertEqual(0x34, LedgerStructType.TYPE_PROVIDE_LEDGER_ACCOUNT_CONTACT)

    def test_values_are_unique(self):
        values = [int(s) for s in LedgerStructType]
        self.assertEqual(len(values), len(set(values)))


class TestValueEnums(TestCase):
    def test_blockchain_family(self):
        self.assertEqual(0x00, BlockchainFamily.BITCOIN)
        self.assertEqual(0x01, BlockchainFamily.ETHEREUM)
        self.assertEqual(0x05, BlockchainFamily.CARDANO)

    def test_trusted_name_type_and_source(self):
        self.assertEqual(0x01, TrustedNameType.EOA)
        self.assertEqual(0x06, TrustedNameType.CONTEXT_ADDRESS)
        self.assertEqual(0x00, TrustedNameSource.LOCAL_ADDRESS_BOOK)
        self.assertEqual(0x07, TrustedNameSource.LESM_ADDRESS_BOOK)

    def test_small_enums(self):
        self.assertEqual(0x02, SimulationType.MESSAGE)
        self.assertEqual(0x02, ProxyDelegatorType.DELEGATOR)
        self.assertEqual(0x01, LesMultisigRole.PROPOSER)
        self.assertEqual(0x05, LkrpStepType.AUTHENTICATE)
