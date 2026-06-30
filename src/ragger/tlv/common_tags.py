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

Common TLV field tags shared by Ledger "Nano certificates and descriptors".

Source of truth:
https://ledgerhq.atlassian.net/wiki/spaces/TrustServices/pages/3843719348/LNS+Arch+Common+Fields+for+Nano+certificates+and+descriptors

IMPORTANT - this enum is intentionally limited to the *globally unique* tags.
The TLV tag space is NOT a single flat namespace: several feature contexts
reuse the same tag IDs with a different meaning.
Those MUST stay in their own per-context enum and must NOT be merged here.
"""

from enum import IntEnum


class LedgerCommonFieldTag(IntEnum):
    """Globally unique TLV tags (Ledger Trust Services spec)."""

    # --- Structure type fields -- always the first tags in a structure
    STRUCTURE_TYPE = 0x01
    VERSION = 0x02

    # --- Common envelope fields -- integrity / source of the structure
    NOT_VALID_AFTER = 0x10
    VALIDITY_INDEX = 0x11
    CHALLENGE = 0x12
    SIGNER_KEY_ID = 0x13
    SIGNER_ALGO = 0x14
    DER_SIGNATURE = 0x15  # MUST be the last tag of the structure
    VALID_UNTIL = 0x16

    # --- Common content fields --
    TRUSTED_NAME = 0x20
    COIN_TYPE = 0x21
    ADDRESS = 0x22
    CHAIN_ID = 0x23
    TICKER = 0x24
    MAGNITUDE = 0x25
    TIME = 0x26
    TX_HASH = 0x27
    DOMAIN_HASH = 0x28
    HMAC_PROOF = 0x29

    # --- Certificate specific fields --
    PUBLIC_KEY_ID = 0x30
    PUBLIC_KEY_USAGE = 0x31
    PUBLIC_KEY_CURVE = 0x32
    PUBLIC_KEY = 0x33
    PUBLIC_KEY_SIGN_ALGO = 0x34
    TARGET_DEVICE = 0x35
    DEPTH = 0x36
