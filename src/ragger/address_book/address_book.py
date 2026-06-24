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

   Generic Address Book test helper.

   The Address Book is an SDK feature shared by coin applications:
   the device binds a human-readable name to a blockchain identifier
   or a Ledger-managed account, and returns HMAC proofs of registration.
   The protocol (TLV tags, sub-command IDs, struct types, chunked
   transport) lives in the SDK and is therefore identical across apps.

   This module encapsulates that protocol so that an app only has to:
     - instantiate a sub-command object (e.g. RegisterIdentity(...))
     - _exchange() the APDUs returned by its get_chunks()

   It is generic over the blockchain family; apps are only expected to bind
   their own family and default values in a thin wrapper.
"""
from enum import IntEnum
from typing import List, Optional

from ragger.bip import pack_derivation_path
from ragger.tlv import (TlvSerializable, BlockchainFamily, LedgerStructType, LedgerCommonFieldTag,
                        CoinInfoFieldTag, SeedIdLkrpFieldTag, AddressBookFieldTag)

# Re-exported; canonical definitions live in ragger.tlv.
__all__ = ["BlockchainFamily", "AddressBookFieldTag"]


class AddressBookSubCommand(IntEnum):
    """Address Book sub-command, carried as APDU P1."""
    SUB_CMD_REGISTER_IDENTITY = 0x01
    SUB_CMD_EDIT_CONTACT_NAME = 0x02
    SUB_CMD_EDIT_IDENTIFIER = 0x03
    SUB_CMD_EDIT_SCOPE = 0x04
    SUB_CMD_REGISTER_LEDGER_ACCOUNT = 0x11
    SUB_CMD_EDIT_LEDGER_ACCOUNT = 0x12
    SUB_CMD_PROVIDE_CONTACT = 0x20
    SUB_CMD_PROVIDE_LEDGER_ACCOUNT_CONTACT = 0x21


GROUP_HANDLE_LENGTH = 64  # group_handle = gid(32) | MAC(K_group, gid)(32)
GID_SIZE = 32  # first half of group_handle, used in HMAC messages
HMAC_PROOF_LENGTH = 32
CONTACT_NAME_MAX_LENGTH = 32  # CONTACT_NAME_LENGTH(33) - 1 null terminator
SCOPE_MAX_LENGTH = 32  # SCOPE_LENGTH(33) - 1 null terminator

# Error messages constants to avoid duplication
ERR_DERIVATION_PATH_REQUIRED = "Derivation path is required"
ERR_IDENTIFIER_REQUIRED = "Identifier is required"
ERR_NEW_IDENTIFIER_REQUIRED = "New identifier is required"
ERR_OLD_IDENTIFIER_REQUIRED = "Old identifier is required"
ERR_CONTACT_NAME_REQUIRED = f"Contact name required (max {CONTACT_NAME_MAX_LENGTH} chars)"
ERR_PREVIOUS_CONTACT_NAME_REQUIRED = f"Previous contact name required (max {CONTACT_NAME_MAX_LENGTH} chars)"
ERR_NEW_CONTACT_NAME_REQUIRED = f"New contact name required (max {CONTACT_NAME_MAX_LENGTH} chars)"
ERR_OLD_ACCOUNT_NAME_REQUIRED = f"Old account name required (max {CONTACT_NAME_MAX_LENGTH} chars)"
ERR_NEW_ACCOUNT_NAME_REQUIRED = f"New account name required (max {CONTACT_NAME_MAX_LENGTH} chars)"
ERR_PREVIOUS_SCOPE_REQUIRED = f"Previous scope required (max {SCOPE_MAX_LENGTH} chars)"
ERR_NEW_SCOPE_REQUIRED = f"New scope required (max {SCOPE_MAX_LENGTH} chars)"
ERR_SCOPE_REQUIRED = f"Scope required (max {SCOPE_MAX_LENGTH} chars)"
ERR_GROUP_HANDLE_LENGTH = f"group_handle must be {GROUP_HANDLE_LENGTH} bytes"
ERR_HMAC_PROOF_LENGTH = f"HMAC_PROOF must be {HMAC_PROOF_LENGTH} bytes"
ERR_HMAC_PROOF_LENGTH_ALT = f"HMAC proof must be {HMAC_PROOF_LENGTH} bytes"
ERR_HMAC_REST_LENGTH = f"HMAC_REST proof must be {HMAC_PROOF_LENGTH} bytes"
ERR_HMAC_REST_LENGTH_ALT = f"HMAC_REST must be {HMAC_PROOF_LENGTH} bytes"
ERR_HMAC_PROOF_REQUIRED = f"hmac_proof must be {HMAC_PROOF_LENGTH} bytes"
ERR_GROUP_HANDLE_HMAC_TOGETHER = "group_handle and hmac_proof must be provided together"


class AddressBookCommand(TlvSerializable):
    """Base class for every Address Book sub-command.

    Each sub-command is its own :class:`~ragger.tlv.TlvSerializable`: it carries
    the data and knows how to :meth:`serialize` itself into a TLV payload. The
    APDU encapsulation (CLA/INS, P1 sub-command selection, P2 chunking and the
    2-byte length prefix) is handled generically by :meth:`get_chunks`, so the app
    only has to ``_exchange()`` the returned chunks.
    """
    # Address Book uses its own CLA/INS, defined by the SDK and shared by all apps.
    CLA = 0xB0
    INS = 0x10
    P2_FIRST_CHUNK = 0x00
    P2_NEXT_CHUNK = 0x80
    CHUNK_SIZE = 0xff

    subcommand: AddressBookSubCommand
    struct_type: LedgerStructType
    blockchain_family: BlockchainFamily
    chain_id: Optional[int]

    def _serialize_network(self) -> bytes:
        """Serialize the CHAIN_ID (optional) + BLOCKCHAIN_FAMILY fields.

        Note: CHAIN_ID is included only when provided.
        """
        payload = b""
        if self.chain_id is not None:
            payload += self.serialize_field(LedgerCommonFieldTag.CHAIN_ID, self.chain_id)
        payload += self.serialize_field(CoinInfoFieldTag.BLOCKCHAIN_FAMILY, self.blockchain_family)
        return payload

    def get_chunks(self, cla: Optional[int] = None, ins: Optional[int] = None) -> List[bytes]:
        """Build the full list of APDUs for this sub-command, ready to _exchange.

        The TLV payload is prefixed with its 2-byte big-endian total length and split over
        ``CHUNK_SIZE`` -byte chunks (a payload fitting in one chunk still carries the prefix).
        P1 selects the sub-command and stays constant.
        P2 flags the first chunk vs continuations.
        """
        cla = self.CLA if cla is None else cla
        ins = self.INS if ins is None else ins
        payload = self.serialize()
        payload = len(payload).to_bytes(2, "big") + payload

        apdus: List[bytes] = []
        p2 = self.P2_FIRST_CHUNK
        while payload:
            chunk = payload[:self.CHUNK_SIZE]
            apdus.append(bytes([cla, ins, self.subcommand, p2, len(chunk)]) + chunk)
            payload = payload[self.CHUNK_SIZE:]
            p2 = self.P2_NEXT_CHUNK
        return apdus


class RegisterIdentity(AddressBookCommand):
    """Register Identity sub-command."""
    subcommand = AddressBookSubCommand.SUB_CMD_REGISTER_IDENTITY
    struct_type = LedgerStructType.TYPE_REGISTER_IDENTITY

    def __init__(self,
                 identifier: bytes,
                 contact_name: str,
                 scope: str,
                 derivation_path: str,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None,
                 group_handle: Optional[bytes] = None,
                 hmac_proof: Optional[bytes] = None) -> None:
        """
        Args:
            identifier: Unique identifier for the contact
            contact_name: Name of the contact (max 32 chars, printable ASCII)
            scope: Scope/namespace for the identifier (max 32 chars)
            derivation_path: BIP32 path used to derive the HMAC key on device
            blockchain_family: Blockchain family of the identifier
            chain_id: Chain ID for the network (optional, typically used for Ethereum-like chains)
            group_handle: Optional 64-byte group handle to link this identifier to an existing group
            hmac_proof: Optional HMAC_NAME required when group_handle is provided
        """
        self.identifier = identifier
        self.contact_name = contact_name
        self.scope = scope
        self.derivation_path = derivation_path
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id
        self.group_handle = group_handle
        self.hmac_proof = hmac_proof

    def serialize(self) -> bytes:
        assert self.contact_name and len(self.contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_CONTACT_NAME_REQUIRED
        assert len(self.identifier) > 0, ERR_IDENTIFIER_REQUIRED
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED
        assert (self.group_handle is None) == (self.hmac_proof is None), \
            ERR_GROUP_HANDLE_HMAC_TOGETHER
        if self.group_handle is not None:
            assert len(self.group_handle) == GROUP_HANDLE_LENGTH, \
                ERR_GROUP_HANDLE_LENGTH
        if self.hmac_proof is not None:
            assert len(self.hmac_proof) == HMAC_PROOF_LENGTH, \
                ERR_HMAC_PROOF_REQUIRED

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.contact_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.SCOPE, self.scope.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.ACCOUNT_IDENTIFIER, self.identifier)
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self._serialize_network()
        if self.group_handle is not None:
            payload += self.serialize_field(AddressBookFieldTag.GROUP_HANDLE, self.group_handle)
        if self.hmac_proof is not None:
            payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_proof)
        return payload


class EditContactName(AddressBookCommand):
    """Edit Contact Name sub-command.

    Only needs group_handle + names + path + HMAC_NAME — no identifier, scope,
    or network required (HMAC_NAME covers only gid + name).
    """
    subcommand = AddressBookSubCommand.SUB_CMD_EDIT_CONTACT_NAME
    struct_type = LedgerStructType.TYPE_EDIT_CONTACT_NAME

    def __init__(self, old_contact_name: str, new_contact_name: str, hmac_proof: bytes,
                 group_handle: bytes, derivation_path: str) -> None:
        """
        Args:
            old_contact_name: Current (old) name of the contact
            new_contact_name: New name to assign to the contact
            hmac_proof: HMAC_NAME from the original Register Identity response
            group_handle: 64-byte group handle received from the Register Identity response
            derivation_path: BIP32 path used to derive the HMAC key on device
        """
        self.old_contact_name = old_contact_name
        self.new_contact_name = new_contact_name
        self.hmac_proof = hmac_proof
        self.group_handle = group_handle
        self.derivation_path = derivation_path

    def serialize(self) -> bytes:
        assert self.old_contact_name and len(self.old_contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_PREVIOUS_CONTACT_NAME_REQUIRED
        assert self.new_contact_name and len(self.new_contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_NEW_CONTACT_NAME_REQUIRED
        assert len(self.group_handle) == GROUP_HANDLE_LENGTH, \
            ERR_GROUP_HANDLE_LENGTH
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED
        assert len(self.hmac_proof) == HMAC_PROOF_LENGTH, ERR_HMAC_PROOF_LENGTH

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.new_contact_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.PREVIOUS_CONTACT_NAME,
                                        self.old_contact_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.GROUP_HANDLE, self.group_handle)
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_proof)
        return payload


class EditIdentifier(AddressBookCommand):
    """Edit Identifier sub-command."""
    subcommand = AddressBookSubCommand.SUB_CMD_EDIT_IDENTIFIER
    struct_type = LedgerStructType.TYPE_EDIT_IDENTIFIER

    def __init__(self,
                 old_identifier: bytes,
                 new_identifier: bytes,
                 contact_name: str,
                 scope: str,
                 derivation_path: str,
                 hmac_proof: bytes,
                 hmac_rest: bytes,
                 group_handle: bytes,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None) -> None:
        """
        Args:
            old_identifier: Current (old) identifier bytes
            new_identifier: New identifier for the contact
            contact_name: Name of the contact (unchanged, for display)
            scope: Scope/namespace for the identifier (unchanged)
            derivation_path: BIP32 path used to derive the HMAC key on device
            hmac_proof: HMAC_NAME from the original Register Identity response
            hmac_rest: HMAC_REST from the original Register Identity response
            group_handle: 64-byte group handle received from the Register Identity response
            blockchain_family: Blockchain family of the identifier
            chain_id: Chain ID for the network (optional, typically used for Ethereum-like chains)
        """
        self.old_identifier = old_identifier
        self.new_identifier = new_identifier
        self.contact_name = contact_name
        self.scope = scope
        self.derivation_path = derivation_path
        self.hmac_proof = hmac_proof
        self.hmac_rest = hmac_rest
        self.group_handle = group_handle
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id

    def serialize(self) -> bytes:
        assert self.contact_name and len(self.contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_CONTACT_NAME_REQUIRED
        assert len(self.group_handle) == GROUP_HANDLE_LENGTH, ERR_GROUP_HANDLE_LENGTH
        assert len(self.old_identifier) > 0, ERR_OLD_IDENTIFIER_REQUIRED
        assert len(self.new_identifier) > 0, ERR_NEW_IDENTIFIER_REQUIRED
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED
        assert len(self.hmac_proof) == HMAC_PROOF_LENGTH, ERR_HMAC_PROOF_LENGTH
        assert len(self.hmac_rest) == HMAC_PROOF_LENGTH, ERR_HMAC_REST_LENGTH

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.contact_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.SCOPE, self.scope.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.ACCOUNT_IDENTIFIER, self.new_identifier)
        payload += self.serialize_field(AddressBookFieldTag.PREVIOUS_IDENTIFIER,
                                        self.old_identifier)
        payload += self.serialize_field(AddressBookFieldTag.GROUP_HANDLE, self.group_handle)
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_proof)
        payload += self.serialize_field(AddressBookFieldTag.HMAC_REST, self.hmac_rest)
        payload += self._serialize_network()
        return payload


class EditScope(AddressBookCommand):
    """Edit Scope sub-command."""
    subcommand = AddressBookSubCommand.SUB_CMD_EDIT_SCOPE
    struct_type = LedgerStructType.TYPE_EDIT_SCOPE

    def __init__(self,
                 old_scope: str,
                 new_scope: str,
                 identifier: bytes,
                 contact_name: str,
                 derivation_path: str,
                 hmac_proof: bytes,
                 hmac_rest: bytes,
                 group_handle: bytes,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None) -> None:
        """
        Args:
            old_scope: Current (old) scope of the contact
            new_scope: New scope to assign to the contact
            identifier: Raw identifier bytes
            contact_name: Name of the contact (unchanged, for display)
            derivation_path: BIP32 path used to derive the HMAC key on device
            hmac_proof: HMAC_NAME from the original Register Identity response
            hmac_rest: HMAC_REST from the original Register Identity response
            group_handle: 64-byte group handle received from the Register Identity response
            blockchain_family: Blockchain family of the identifier
            chain_id: Chain ID for the network (optional, typically used for Ethereum-like chains)
        """
        self.old_scope = old_scope
        self.new_scope = new_scope
        self.identifier = identifier
        self.contact_name = contact_name
        self.derivation_path = derivation_path
        self.hmac_proof = hmac_proof
        self.hmac_rest = hmac_rest
        self.group_handle = group_handle
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id

    def serialize(self) -> bytes:
        assert self.contact_name and len(self.contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_CONTACT_NAME_REQUIRED
        assert len(self.group_handle) == GROUP_HANDLE_LENGTH, ERR_GROUP_HANDLE_LENGTH
        assert self.old_scope and len(self.old_scope) <= SCOPE_MAX_LENGTH, \
            ERR_PREVIOUS_SCOPE_REQUIRED
        assert self.new_scope and len(self.new_scope) <= SCOPE_MAX_LENGTH, \
            ERR_NEW_SCOPE_REQUIRED
        assert len(self.identifier) > 0, ERR_IDENTIFIER_REQUIRED
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED
        assert len(self.hmac_proof) == HMAC_PROOF_LENGTH, ERR_HMAC_PROOF_LENGTH
        assert len(self.hmac_rest) == HMAC_PROOF_LENGTH, ERR_HMAC_REST_LENGTH

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.contact_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.SCOPE, self.new_scope.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.ACCOUNT_IDENTIFIER, self.identifier)
        payload += self.serialize_field(AddressBookFieldTag.PREVIOUS_SCOPE,
                                        self.old_scope.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.GROUP_HANDLE, self.group_handle)
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_proof)
        payload += self.serialize_field(AddressBookFieldTag.HMAC_REST, self.hmac_rest)
        payload += self._serialize_network()
        return payload


class RegisterLedgerAccount(AddressBookCommand):
    """Register Ledger Account sub-command."""
    subcommand = AddressBookSubCommand.SUB_CMD_REGISTER_LEDGER_ACCOUNT
    struct_type = LedgerStructType.TYPE_REGISTER_LEDGER_ACCOUNT

    def __init__(self,
                 contact_name: str,
                 derivation_path: str,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None) -> None:
        """
        Args:
            contact_name: Name for this contact
            derivation_path: BIP32 derivation path as string (e.g., "m/44'/60'/0'/0/0")
            blockchain_family: Blockchain family of the account
            chain_id: Chain ID for the network (optional, typically used for Ethereum-like chains)
        """
        self.contact_name = contact_name
        self.derivation_path = derivation_path
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id

    def serialize(self) -> bytes:
        assert self.contact_name and len(self.contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_CONTACT_NAME_REQUIRED
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.contact_name.encode('utf-8'))
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self._serialize_network()
        return payload


class EditLedgerAccount(AddressBookCommand):
    """Edit Ledger Account sub-command."""
    subcommand = AddressBookSubCommand.SUB_CMD_EDIT_LEDGER_ACCOUNT
    struct_type = LedgerStructType.TYPE_EDIT_LEDGER_ACCOUNT

    def __init__(self,
                 old_account_name: str,
                 new_account_name: str,
                 derivation_path: str,
                 hmac_proof: bytes,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None) -> None:
        """
        Args:
            old_account_name: Current name of the account
            new_account_name: New name to assign to the account
            derivation_path: BIP32 path used to derive the HMAC key on device
            hmac_proof: HMAC Proof of Registration from the previous registration
            blockchain_family: Blockchain family of the account
            chain_id: Chain ID for the network (optional, typically used for Ethereum-like chains)
        """
        self.old_account_name = old_account_name
        self.new_account_name = new_account_name
        self.derivation_path = derivation_path
        self.hmac_proof = hmac_proof
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id

    def serialize(self) -> bytes:
        assert self.old_account_name and len(self.old_account_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_OLD_ACCOUNT_NAME_REQUIRED
        assert self.new_account_name and len(self.new_account_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_NEW_ACCOUNT_NAME_REQUIRED
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED
        assert len(self.hmac_proof) == HMAC_PROOF_LENGTH, ERR_HMAC_PROOF_LENGTH_ALT

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.new_account_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.PREVIOUS_CONTACT_NAME,
                                        self.old_account_name.encode('utf-8'))
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_proof)
        payload += self._serialize_network()
        return payload


class ProvideContact(AddressBookCommand):
    """Provide Contact sub-command.

    Delivers a previously registered contact to the device so that the
    application can substitute the contact name for the raw identifier during
    transaction review. No UI is displayed.
    """
    subcommand = AddressBookSubCommand.SUB_CMD_PROVIDE_CONTACT
    struct_type = LedgerStructType.TYPE_PROVIDE_CONTACT

    def __init__(self,
                 identifier: bytes,
                 group_handle: bytes,
                 hmac_name: bytes,
                 hmac_rest: bytes,
                 contact_name: str,
                 scope: str,
                 derivation_path: str,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None) -> None:
        """
        Args:
            identifier:         Raw identifier bytes
            group_handle:    64-byte group handle from the Register Identity response
            hmac_name:       HMAC_PROOF (32 B) from the Register Identity response
            hmac_rest:       HMAC_REST  (32 B) from the Register Identity response
            contact_name:    Human-readable name bound to the identifier
            scope:           Scope/namespace for the identifier
            derivation_path: BIP32 path used to derive the HMAC key on device
            blockchain_family: Blockchain family of the identifier
            chain_id:        Chain ID for the network (optional, typically used for Ethereum-like chains)
        """
        self.identifier = identifier
        self.group_handle = group_handle
        self.hmac_name = hmac_name
        self.hmac_rest = hmac_rest
        self.contact_name = contact_name
        self.scope = scope
        self.derivation_path = derivation_path
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id

    def serialize(self) -> bytes:
        assert self.contact_name and len(self.contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_CONTACT_NAME_REQUIRED
        assert self.scope and len(self.scope) <= SCOPE_MAX_LENGTH, \
            ERR_SCOPE_REQUIRED
        assert len(self.identifier) > 0, ERR_IDENTIFIER_REQUIRED
        assert len(self.group_handle) == GROUP_HANDLE_LENGTH, \
            ERR_GROUP_HANDLE_LENGTH
        assert len(self.hmac_name) == HMAC_PROOF_LENGTH, \
            ERR_HMAC_PROOF_LENGTH
        assert len(self.hmac_rest) == HMAC_PROOF_LENGTH, \
            ERR_HMAC_REST_LENGTH_ALT
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.contact_name.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.SCOPE, self.scope.encode('utf-8'))
        payload += self.serialize_field(AddressBookFieldTag.ACCOUNT_IDENTIFIER, self.identifier)
        payload += self.serialize_field(AddressBookFieldTag.GROUP_HANDLE, self.group_handle)
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self._serialize_network()
        payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_name)
        payload += self.serialize_field(AddressBookFieldTag.HMAC_REST, self.hmac_rest)
        return payload


class ProvideLedgerAccountContact(AddressBookCommand):
    """Provide Ledger Account Contact sub-command.

    Unlike an Identity contact, a Ledger Account contact has no external
    identifier, no group_handle, no hmac_rest, and no scope: the device derives the
    identifier internally from the derivation_path and verifies authenticity via
    hmac_proof (the HMAC Proof of Registration from RegisterLedgerAccount).
    """
    subcommand = AddressBookSubCommand.SUB_CMD_PROVIDE_LEDGER_ACCOUNT_CONTACT
    struct_type = LedgerStructType.TYPE_PROVIDE_LEDGER_ACCOUNT_CONTACT

    def __init__(self,
                 hmac_proof: bytes,
                 contact_name: str,
                 derivation_path: str,
                 blockchain_family: BlockchainFamily,
                 chain_id: Optional[int] = None) -> None:
        """
        Args:
            hmac_proof:      32-byte HMAC proof from the Register Ledger Account response
            contact_name:    Human-readable account name
            derivation_path: BIP32 path used to derive the identifier and the HMAC key
            blockchain_family: Blockchain family of the account
            chain_id:        Chain ID for the network (optional, typically used for Ethereum-like chains)
        """
        self.hmac_proof = hmac_proof
        self.contact_name = contact_name
        self.derivation_path = derivation_path
        self.blockchain_family = blockchain_family
        self.chain_id = chain_id

    def serialize(self) -> bytes:
        assert self.contact_name and len(self.contact_name) <= CONTACT_NAME_MAX_LENGTH, \
            ERR_CONTACT_NAME_REQUIRED
        assert len(self.hmac_proof) == HMAC_PROOF_LENGTH, \
            ERR_HMAC_PROOF_REQUIRED
        assert self.derivation_path, ERR_DERIVATION_PATH_REQUIRED

        path_bytes = pack_derivation_path(self.derivation_path)

        payload: bytes = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, self.struct_type)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, 1)
        payload += self.serialize_field(AddressBookFieldTag.CONTACT_NAME,
                                        self.contact_name.encode('utf-8'))
        payload += self.serialize_field(SeedIdLkrpFieldTag.DERIVATION_PATH, path_bytes)
        payload += self._serialize_network()
        payload += self.serialize_field(LedgerCommonFieldTag.HMAC_PROOF, self.hmac_proof)
        return payload
