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

   Transverse enums of the Trust Services "Common Fields" specification.
   These value types are shared by several certificates / descriptors, hence
   their home here next to the TLV primitives rather than in a feature module.
"""
from enum import IntEnum


class LedgerStructType(IntEnum):
    """Structure type discriminator for Ledger Trust Services (tag STRUCTURE_TYPE)."""
    TYPE_CERTIFICATE = 0x01
    TYPE_NFT_COLLECTION_NAME = 0x02
    TYPE_DOMAIN_TRUSTED_NAME = 0x03
    TYPE_ERC20_INFO = 0x04
    TYPE_EVM_FUNCTION_INFO = 0x05
    TYPE_COIN_INFO = 0x06
    TYPE_SEED_ID_AUTHENTICATION_CHALLENGE = 0x07
    TYPE_DYNAMIC_NETWORK = 0x08
    TYPE_TX_SIMULATION = 0x09
    TYPE_SOLANA_SWAP_TEMPLATE = 0x0a
    TYPE_VERIFIABLE_ADDRESS = 0x0b
    TYPE_LKRP_TOPIC = 0x0c
    TYPE_GATED_SIGNING = 0x0d
    TYPE_LKRP_STEP = 0x0e
    TYPE_PROXY = 0x26
    TYPE_LESM_ACCOUNT_INFO = 0x27
    TYPE_ALEO_INTENT = 0x28
    TYPE_ALEO_PREPARED_REQUEST = 0x29
    TYPE_ALEO_REQUEST_SIGNATURE = 0x2a
    TYPE_PERPS_METADATA = 0x2b
    TYPE_PERPS_ACTION = 0x2c
    TYPE_REGISTER_IDENTITY = 0x2d
    TYPE_EDIT_CONTACT_NAME = 0x2e
    TYPE_REGISTER_LEDGER_ACCOUNT = 0x2f
    TYPE_EDIT_LEDGER_ACCOUNT = 0x30
    TYPE_EDIT_IDENTIFIER = 0x31
    TYPE_EDIT_SCOPE = 0x32
    TYPE_PROVIDE_CONTACT = 0x33
    TYPE_PROVIDE_LEDGER_ACCOUNT_CONTACT = 0x34


class TrustedNameType(IntEnum):
    """Trusted name account type (tag TRUSTED_NAME_TYPE)."""
    EOA = 0x01
    SMART_CONTRACT = 0x02
    COLLECTION = 0x03
    TOKEN = 0x04
    WALLET = 0x05
    CONTEXT_ADDRESS = 0x06
    CCD_CONTEXT_ADDRESS = 0x07


class TrustedNameSource(IntEnum):
    """Trusted name namespace (tag TRUSTED_NAME_SOURCE)."""
    LOCAL_ADDRESS_BOOK = 0x00
    CRYPTO_ASSET_LIST = 0x01
    ENS = 0x02
    UNSTOPPABLE_DOMAIN = 0x03
    FREENAME = 0x04
    DNS = 0x05
    DYNAMIC_RESOLVER = 0x06
    LESM_ADDRESS_BOOK = 0x07


class BlockchainFamily(IntEnum):
    """Blockchain family (tag BLOCKCHAIN_FAMILY)."""
    BITCOIN = 0x00
    ETHEREUM = 0x01
    SOLANA = 0x02
    POLKADOT = 0x03
    COSMOS = 0x04
    CARDANO = 0x05


class SimulationType(IntEnum):
    """TX simulation type (tag SIMULATION_TYPE)."""
    TRANSACTION = 0x00
    TYPED_MESSAGE = 0x01
    MESSAGE = 0x02


class ProxyDelegatorType(IntEnum):
    """Proxy/delegator type (tag DELEGATION_TYPE)."""
    PROXY = 0x00
    ISSUED_FROM_FACTORY = 0x01
    DELEGATOR = 0x02


class LesMultisigRole(IntEnum):
    """LES Multisig address role (tag ROLE)."""
    SIGNER = 0x00
    PROPOSER = 0x01


class LkrpStepType(IntEnum):
    """LKRP intent step type (tag STEP_TYPE)."""
    HEADER = 0x00
    ADD_MEMBER = 0x01
    REMOVE_MEMBER = 0x02
    SET_TOPIC = 0x03
    DISPLAY = 0x04
    AUTHENTICATE = 0x05
