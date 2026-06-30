"""
Copyright 2026 Ledger SAS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Feature-specific TLV field tags (Trust Services spec).

Each structure type owns its own tag namespace. Tags are globally unique
ACROSS features, EXCEPT where a feature deliberately reuses a common tag
or where a feature splits into several
sub-structures that reuse IDs internally. The latter is why Perps
is modelled as several enums rather than one: ASSET_ID is 0xd1 in most
sub-structures but 0xe1 in the Order / UpdateIsolatedMargin tables.
"""

from enum import IntEnum


class TrustedNameFieldTag(IntEnum):
    """Trusted domain name specific fields."""

    TRUSTED_NAME_TYPE = 0x70
    TRUSTED_NAME_SOURCE = 0x71
    TRUSTED_NAME_NFT_ID = 0x72
    TRUSTED_NAME_SOURCE_CONTRACT = 0x73
    TRUSTED_NAME_OWNER = 0x74
    TRUSTED_NAME_OWNER_DERIVATION_PATH = 0x75


class EvmFunctionFieldTag(IntEnum):
    """EVM function info / plugin descriptor specific fields."""

    EVM_FUNCTION_SELECTOR = 0x40
    IMPLEMENTATION_ADDRESSES = 0x41
    DELEGATION_TYPE = 0x42


class CoinInfoFieldTag(IntEnum):
    """Coin info / dynamic network specific fields."""

    COIN_CONFIG = 0x50
    BLOCKCHAIN_FAMILY = 0x51
    NETWORK_NAME = 0x52
    NETWORK_ICON_HASH = 0x53


class SeedIdLkrpFieldTag(IntEnum):
    """SeedID / LKRP specific fields."""

    PROTOCOL_VERSION = 0x60
    ADDRESS_SIGNATURE = 0x61
    TOPIC_PARENT = 0x62
    TOPIC_DICTIONARY = 0x63
    TOPIC_CONTROL_DISPLAY = 0x64
    TOPIC_NEW_AUTHORITY = 0x65
    STEP_TYPE = 0x66
    STEP_COUNT = 0x67
    DISPLAY = 0x68
    DERIVATION_PATH = 0x69
    MEMBER = 0x6A
    TOPIC_HASH = 0x6B
    DISPLAYED_STEP_COUNT = 0x6C
    MEMBER_COUNT = 0x6D


class TxSimulationFieldTag(IntEnum):
    """TX Simulation specific fields."""

    NORMALIZED_RISK = 0x80
    NORMALIZED_CATEGORY = 0x81
    PROVIDER_MESSAGE = 0x82
    TINY_URL = 0x83
    SIMULATION_TYPE = 0x84


class SwapTemplateFieldTag(IntEnum):
    """Solana swap template specific fields."""

    TEMPLATE_ID = 0x90
    PROGRAM_ID = 0x91
    DISCRIMINATOR = 0x92
    AMOUNT_SIZE = 0x93
    AMOUNT_OFFSET = 0x94
    AMOUNT_RULES = 0x95
    ASSET_ACCOUNT_INDEX = 0x96
    ASSET_ATA_INDEX = 0x97
    RECIPIENT_ACCOUNT_INDEX = 0x98
    RECIPIENT_ATA_INDEX = 0x99


class LesMultisigFieldTag(IntEnum):
    """LES Multisig specific fields."""

    THRESHOLD = 0xA0
    SIGNERS_COUNT = 0xA1
    ROLE = 0xA2


class AleoFieldTag(IntEnum):
    """Aleo application specific fields."""

    MAX_BASE_FEE = 0xB0
    MAX_PRIORITY_FEE = 0xB1
    FEE_FUNCTION_NAME = 0xB2
    FEE_PROGRAM_ID = 0xB3
    REQUEST = 0xB4
    PROGRAM_ID = 0xB5
    FUNCTION_NAME = 0xB6
    INPUT_COUNT = 0xB7
    INPUT_VALUES = 0xB8
    INPUT_TYPES = 0xB9
    NESTED_CALL_COUNT = 0xBA
    RECORD_COMMITMENTS_COUNT = 0xBC
    RECORD_COMMITMENT = 0xBD
    TVK = 0xBF
    TPK = 0xC0
    GAMMAS_COUNT = 0xC1
    GAMMAS = 0xC2
    NETWORK_ID = 0xC3
    PROGRAM_CHECKSUM = 0xC4
    R_HINT = 0xC5


# --- Perps (HyperLiquid) specific fields -------------------------
# Split into one enum per sub-structure: the action sub-structures reuse tag
# IDs (ASSET_ID is 0xd1 in most tables but 0xe1 in Order / UpdateIsolatedMargin,
# LEVERAGE is 0xd5 in the context but 0xed in the leverage action, ...), so a
# single flat enum is impossible.


class PerpsContextFieldTag(IntEnum):
    """Perps context descriptor."""

    ACTION_TYPE = 0xD0
    ASSET_ID = 0xD1
    NETWORK_TYPE = 0xD2
    BUILDER_ADDRESS = 0xD3
    MARGIN = 0xD4
    LEVERAGE = 0xD5


class PerpsActionFieldTag(IntEnum):
    """Perps action wrapper."""

    ACTION_TYPE = 0xD0
    NONCE = 0xDA
    ACTION_STRUCTURE = 0xDB


class PerpsCreateOrderFieldTag(IntEnum):
    """Perps create_order action structure."""

    ORDER = 0xDD
    GROUPING = 0xEA
    BUILDER = 0xEB
    BUILDER_ADDRESS = 0xD3
    BUILDER_FEE = 0xEC


class PerpsUpdateOrderFieldTag(IntEnum):
    """Perps update_order action structure."""

    UPDATE_ORDER = 0xD8
    ORDER = 0xDD
    ORDER_ID = 0xDC


class PerpsCancelOrderFieldTag(IntEnum):
    """Perps cancel_order action structure."""

    CANCEL_ORDER = 0xD9
    ASSET_ID = 0xD1
    ORDER_ID = 0xDC


class PerpsLeverageFieldTag(IntEnum):
    """Perps leverage action structure."""

    ASSET_ID = 0xD1
    IS_CROSS = 0xDE
    LEVERAGE = 0xED


class PerpsOrderFieldTag(IntEnum):
    """Perps Order structure, incl. its ORDER_DETAIL tags.

    NB: here ASSET_ID is 0xe1 (vs 0xd1 in the other sub-structures).
    """

    ORDER_TYPE = 0xE0
    ASSET_ID = 0xE1
    IS_BUY = 0xE2
    PRICE = 0xE3
    SIZE = 0xE4
    REDUCE_ONLY = 0xE5
    ORDER_DETAIL = 0xD7
    TIF = 0xE6
    TRIGGER_MARKET = 0xE7
    TRIGGER_PRICE = 0xE8
    TRIGGER_TYPE = 0xE9


class PerpsApprovalBuilderFeeFieldTag(IntEnum):
    """Perps ApprovalBuilderFee action structure."""

    MAX_BASE_FEE = 0xB0
    BUILDER_ADDRESS = 0xD3


class PerpsUpdateIsolatedMarginFieldTag(IntEnum):
    """Perps UpdateIsolatedMargin action structure."""

    ASSET_ID = 0xE1
    IS_BUY = 0xE2
    NTLI = 0xD6


class AddressBookFieldTag(IntEnum):
    """Address Book specific fields ."""

    CONTACT_NAME = 0xF0
    SCOPE = 0xF1
    ACCOUNT_IDENTIFIER = 0xF2
    PREVIOUS_CONTACT_NAME = 0xF3
    PREVIOUS_IDENTIFIER = 0xF4
    PREVIOUS_SCOPE = 0xF5
    GROUP_HANDLE = 0xF6
    HMAC_REST = 0xF7
