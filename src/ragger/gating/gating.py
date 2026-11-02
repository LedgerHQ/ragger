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

Generic Gating test helper.

Gating is an SDK feature shared by coin applications: a signed descriptor tells the
device that a safer signing path exists for the transaction about to be blind signed,
and the device displays a prelude pointing to it. The protocol (TLV tags, struct type,
CLA/INS, chunked transport) lives in the SDK and is therefore identical across apps;
only the meaning of ADDRESS, CHAIN_ID and SELECTOR depends on the blockchain.

An app only has to build a GatingDescriptor, send the PKI certificate of the signer,
then _exchange() the APDUs returned by get_chunks().
"""

from enum import IntEnum

from ragger.pki import SigningPartner
from ragger.tlv import GatingFieldTag, LedgerCommonFieldTag, LedgerStructType, TlvSerializable

# CLA/INS defined by the SDK and shared by all apps.
GATING_CLA = 0xB0
GATING_INS = 0x12
GATING_VERSION = 0x01


class GatingSubCommand(IntEnum):
    """Gating sub-command, carried as APDU P1."""

    SUB_CMD_PROVIDE_DESCRIPTOR = 0x01


class GatingTxType(IntEnum):
    """Kind of operation the descriptor applies to (tag TX_TYPE)."""

    TRANSACTION = 0x00
    MESSAGE = 0x01


class GatingDescriptor(TlvSerializable):
    """Gating descriptor, serialized as a TLV payload and sent with the SDK Gating command."""

    P2_FIRST_CHUNK = 0x00
    P2_NEXT_CHUNK = 0x80
    CHUNK_SIZE = 0xFF

    def __init__(
        self,
        tx_type: GatingTxType,
        address: bytes,
        intro_message: str,
        tiny_url: str,
        chain_id: int | None = None,
        selector: bytes | None = None,
        signer: SigningPartner | None = None,
        signature: bytes | None = None,
    ) -> None:
        """
        Args:
            tx_type: Kind of operation the descriptor applies to.
            address: Contract / program address, in the blockchain raw format.
            intro_message: Message displayed by the prelude.
            tiny_url: URL encoded in the prelude QR code.
            chain_id: Network identifier, when the blockchain has one.
            selector: Function selector, schema hash, ... depending on the blockchain.
            signer: PKI partner signing the descriptor, used when no signature is given.
            signature: Explicit signature, e.g. to send a tampered one.
        """
        self.tx_type = tx_type
        self.address = address
        self.intro_message = intro_message
        self.tiny_url = tiny_url
        self.chain_id = chain_id
        self.selector = selector
        self.signer = signer
        self.signature = signature

    def serialize(self) -> bytes:
        payload = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, LedgerStructType.TYPE_GATED_SIGNING)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, GATING_VERSION)
        payload += self.serialize_field(GatingFieldTag.TX_TYPE, self.tx_type)
        payload += self.serialize_field(LedgerCommonFieldTag.ADDRESS, self.address)
        if self.chain_id is not None:
            payload += self.serialize_field(LedgerCommonFieldTag.CHAIN_ID, self.chain_id.to_bytes(8, "big"))
        payload += self.serialize_field(GatingFieldTag.INTRO_MSG, self.intro_message.encode("utf-8"))
        payload += self.serialize_field(GatingFieldTag.TINY_URL, self.tiny_url.encode("utf-8"))
        if self.selector is not None:
            payload += self.serialize_field(GatingFieldTag.SELECTOR, self.selector)

        signature = self.signature
        if signature is None:
            if self.signer is None:
                raise ValueError("Either a signer or a signature is required")
            signature = self.signer.sign(payload)
        payload += self.serialize_field(LedgerCommonFieldTag.DER_SIGNATURE, signature)
        return payload

    def get_chunks(self) -> list[bytes]:
        """Build the full list of SDK APDUs for this descriptor, ready to _exchange.

        The TLV payload is prefixed with its 2-byte big-endian total length and split over
        ``CHUNK_SIZE`` -byte chunks (a payload fitting in one chunk still carries the prefix).
        P2 flags the first chunk vs continuations.
        """
        payload = self.serialize()
        payload = len(payload).to_bytes(2, "big") + payload

        apdus: list[bytes] = []
        p2 = self.P2_FIRST_CHUNK
        while payload:
            chunk = payload[: self.CHUNK_SIZE]
            apdus.append(bytes([GATING_CLA, GATING_INS, GatingSubCommand.SUB_CMD_PROVIDE_DESCRIPTOR, p2, len(chunk)]) + chunk)
            payload = payload[self.CHUNK_SIZE :]
            p2 = self.P2_NEXT_CHUNK
        return apdus
