from unittest import TestCase

from ragger.tlv import (
    TrustedNameFieldTag,
    EvmFunctionFieldTag,
    CoinInfoFieldTag,
    SeedIdLkrpFieldTag,
    TxSimulationFieldTag,
    SwapTemplateFieldTag,
    LesMultisigFieldTag,
    AleoFieldTag,
    PerpsContextFieldTag,
    PerpsActionFieldTag,
    PerpsCreateOrderFieldTag,
    PerpsUpdateOrderFieldTag,
    PerpsCancelOrderFieldTag,
    PerpsLeverageFieldTag,
    PerpsOrderFieldTag,
    PerpsApprovalBuilderFeeFieldTag,
    PerpsUpdateIsolatedMarginFieldTag,
    AddressBookFieldTag,
)

ALL_FEATURE_ENUMS = [
    TrustedNameFieldTag,
    EvmFunctionFieldTag,
    CoinInfoFieldTag,
    SeedIdLkrpFieldTag,
    TxSimulationFieldTag,
    SwapTemplateFieldTag,
    LesMultisigFieldTag,
    AleoFieldTag,
    PerpsContextFieldTag,
    PerpsActionFieldTag,
    PerpsCreateOrderFieldTag,
    PerpsUpdateOrderFieldTag,
    PerpsCancelOrderFieldTag,
    PerpsLeverageFieldTag,
    PerpsOrderFieldTag,
    PerpsApprovalBuilderFeeFieldTag,
    PerpsUpdateIsolatedMarginFieldTag,
    AddressBookFieldTag,
]


class TestFeatureFieldTags(TestCase):
    def test_known_values(self):
        self.assertEqual(0x70, TrustedNameFieldTag.TRUSTED_NAME_TYPE)
        self.assertEqual(0x40, EvmFunctionFieldTag.EVM_FUNCTION_SELECTOR)
        self.assertEqual(0x51, CoinInfoFieldTag.BLOCKCHAIN_FAMILY)
        self.assertEqual(0x84, TxSimulationFieldTag.SIMULATION_TYPE)
        self.assertEqual(0x90, SwapTemplateFieldTag.TEMPLATE_ID)
        self.assertEqual(0xA0, LesMultisigFieldTag.THRESHOLD)

    def test_no_accidental_alias_within_each_enum(self):
        # Two distinct names sharing a value would silently alias in an IntEnum.
        for enum in ALL_FEATURE_ENUMS:
            names = list(enum.__members__)
            canonical = list(enum)
            self.assertEqual(
                len(names), len(canonical), f"{enum.__name__} has an aliased member"
            )

    def test_derivation_path_is_0x69(self):
        # DERIVATION_PATH 0x69 is shared by SeedID/LKRP and the Address Book.
        self.assertEqual(0x69, SeedIdLkrpFieldTag.DERIVATION_PATH)

    def test_perps_asset_id_contextual_reuse(self):
        # ASSET_ID is 0xd1 in most sub-structures but 0xe1 in Order / margin tables.
        self.assertEqual(0xD1, PerpsContextFieldTag.ASSET_ID)
        self.assertEqual(0xD1, PerpsCancelOrderFieldTag.ASSET_ID)
        self.assertEqual(0xD1, PerpsLeverageFieldTag.ASSET_ID)
        self.assertEqual(0xE1, PerpsOrderFieldTag.ASSET_ID)
        self.assertEqual(0xE1, PerpsUpdateIsolatedMarginFieldTag.ASSET_ID)

    def test_perps_leverage_contextual_reuse(self):
        self.assertEqual(0xD5, PerpsContextFieldTag.LEVERAGE)
        self.assertEqual(0xED, PerpsLeverageFieldTag.LEVERAGE)

    def test_max_base_fee_shared_across_features(self):
        # Same name and value (0xb0) in two different features (own namespaces).
        self.assertEqual(0xB0, AleoFieldTag.MAX_BASE_FEE)
        self.assertEqual(0xB0, PerpsApprovalBuilderFeeFieldTag.MAX_BASE_FEE)

    def test_is_buy_name_uniform_across_perps_substructures(self):
        self.assertEqual(0xE2, PerpsOrderFieldTag.IS_BUY)
        self.assertEqual(0xE2, PerpsUpdateIsolatedMarginFieldTag.IS_BUY)


class TestAddressBookFieldTag(TestCase):
    def test_specific_field_values(self):
        self.assertEqual(0xF0, AddressBookFieldTag.CONTACT_NAME)
        self.assertEqual(0xF1, AddressBookFieldTag.SCOPE)
        self.assertEqual(0xF2, AddressBookFieldTag.ACCOUNT_IDENTIFIER)
        self.assertEqual(0xF3, AddressBookFieldTag.PREVIOUS_CONTACT_NAME)
        self.assertEqual(0xF4, AddressBookFieldTag.PREVIOUS_IDENTIFIER)
        self.assertEqual(0xF5, AddressBookFieldTag.PREVIOUS_SCOPE)
        self.assertEqual(0xF6, AddressBookFieldTag.GROUP_HANDLE)
        self.assertEqual(0xF7, AddressBookFieldTag.HMAC_REST)
