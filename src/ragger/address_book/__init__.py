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
from .address_book import (
    BlockchainFamily,
    AddressBookSubCommand,
    AddressBookFieldTag,
    AddressBookCommand,
    RegisterIdentity,
    EditContactName,
    EditIdentifier,
    EditScope,
    RegisterLedgerAccount,
    EditLedgerAccount,
    ProvideContact,
    ProvideLedgerAccountContact,
    GROUP_HANDLE_LENGTH,
    GID_SIZE,
    HMAC_PROOF_LENGTH,
    CONTACT_NAME_MAX_LENGTH,
    SCOPE_MAX_LENGTH,
)

__all__ = [
    "BlockchainFamily",
    "AddressBookSubCommand",
    "AddressBookFieldTag",
    "AddressBookCommand",
    "RegisterIdentity",
    "EditContactName",
    "EditIdentifier",
    "EditScope",
    "RegisterLedgerAccount",
    "EditLedgerAccount",
    "ProvideContact",
    "ProvideLedgerAccountContact",
    "GROUP_HANDLE_LENGTH",
    "GID_SIZE",
    "HMAC_PROOF_LENGTH",
    "CONTACT_NAME_MAX_LENGTH",
    "SCOPE_MAX_LENGTH",
]
