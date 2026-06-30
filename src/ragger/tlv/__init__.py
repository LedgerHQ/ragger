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
"""

from .serializable import TlvSerializable, der_encode, format_tlv
from .common_tags import LedgerCommonFieldTag
from .enums import (
    LedgerStructType,
    BlockchainFamily,
    TrustedNameType,
    TrustedNameSource,
    SimulationType,
    ProxyDelegatorType,
    LesMultisigRole,
    LkrpStepType,
)
from .feature_tags import (
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

__all__ = [
    # TLV primitives
    "TlvSerializable",
    "der_encode",
    "format_tlv",
    # Common registry (§3.2.1-3.2.4)
    "LedgerCommonFieldTag",
    # Transverse value enums (§3.3)
    "LedgerStructType",
    "BlockchainFamily",
    "TrustedNameType",
    "TrustedNameSource",
    "SimulationType",
    "ProxyDelegatorType",
    "LesMultisigRole",
    "LkrpStepType",
    # Feature-specific field tags (§3.2.6-3.2.15)
    "TrustedNameFieldTag",
    "EvmFunctionFieldTag",
    "CoinInfoFieldTag",
    "SeedIdLkrpFieldTag",
    "TxSimulationFieldTag",
    "SwapTemplateFieldTag",
    "LesMultisigFieldTag",
    "AleoFieldTag",
    "PerpsContextFieldTag",
    "PerpsActionFieldTag",
    "PerpsCreateOrderFieldTag",
    "PerpsUpdateOrderFieldTag",
    "PerpsCancelOrderFieldTag",
    "PerpsLeverageFieldTag",
    "PerpsOrderFieldTag",
    "PerpsApprovalBuilderFeeFieldTag",
    "PerpsUpdateIsolatedMarginFieldTag",
    "AddressBookFieldTag",
]
