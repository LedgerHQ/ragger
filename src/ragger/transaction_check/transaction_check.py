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

Generic Transaction Check test helper.

Transaction Check is an SDK feature shared by coin applications: a security
provider assesses a transaction (or typed data), and the device displays the
risk during the review. The protocol (descriptor TLV, signature, CLA/INS,
chunked transport, opt-in request) lives in the SDK and is therefore identical
across apps.

This module encapsulates that protocol so that an app only has to:
  - instantiate a :class:`TransactionCheck` descriptor with its own address format and
    its PKI signing partner
  - _exchange() the APDUs returned by its get_chunks()
  - _exchange() :func:`get_opt_in_apdu` for the opt-in request
"""

from enum import IntEnum

from ragger.pki import SigningPartner
from ragger.tlv import LedgerCommonFieldTag, LedgerStructType, SimulationType, TlvSerializable, TxSimulationFieldTag

# Re-exported; canonical definition lives in ragger.tlv.
__all__ = ["SimulationType"]

# CLA/INS defined by the SDK and shared by all apps.
TRANSACTION_CHECK_CLA = 0xB0
TRANSACTION_CHECK_INS = 0x11

TRANSACTION_CHECK_VERSION = 1
TRANSACTION_CHECK_HASH_LENGTH = 32

ERR_TX_HASH_LENGTH = f"tx_hash must be {TRANSACTION_CHECK_HASH_LENGTH} bytes"
ERR_DOMAIN_HASH_LENGTH = f"domain_hash must be {TRANSACTION_CHECK_HASH_LENGTH} bytes"
ERR_SIGNATURE_REQUIRED = "Either a partner or a signature is required"


class TransactionCheckSubCommand(IntEnum):
    """Transaction Check sub-command, carried as APDU P1."""

    SUB_CMD_DESCRIPTOR = 0x00
    SUB_CMD_OPT_IN = 0x01


class TransactionCheckRisk(IntEnum):
    """Risk level assessed by the provider (tag NORMALIZED_RISK)."""

    BENIGN = 0x00
    WARNING = 0x01
    MALICIOUS = 0x02


class TransactionCheckCategory(IntEnum):
    """Risk category assessed by the provider (tag NORMALIZED_CATEGORY)."""

    NA = 0x00
    OTHERS = 0x01
    ADDRESS = 0x02
    DAPP = 0x03
    LOSING_OPERATION = 0x04


class TransactionCheck(TlvSerializable):
    """Transaction Check descriptor, signed by the provider.

    :meth:`serialize` gives the signed TLV payload, whatever the transport.
    :meth:`get_chunks` gives the APDUs of the SDK transport (CLA 0xB0, INS 0x11),
    the same chunking as the Address Book.
    """

    P2_FIRST_CHUNK = 0x00
    P2_NEXT_CHUNK = 0x80
    CHUNK_SIZE = 0xFF

    def __init__(
        self,
        address: bytes | str,
        tx_hash: bytes,
        risk: TransactionCheckRisk | int,
        category: TransactionCheckCategory | int,
        tiny_url: str,
        partner: SigningPartner | None = None,
        simulation_type: SimulationType | int = SimulationType.TRANSACTION,
        chain_id: int | None = None,
        domain_hash: bytes | None = None,
        provider_message: str | None = None,
        signature: bytes | None = None,
    ) -> None:
        """
        Args:
            address: Signer address, in the chain format (raw bytes or text encoding).
            tx_hash: Hash of the transaction or message, as computed by the app.
            risk: Risk level.
            category: Risk category.
            tiny_url: Report URL.
            partner: Provider PKI signing partner (key usage TX_SIMU_SIGNER), signing every
                TLV but the signature, used when no signature is given.
            simulation_type: Transaction or typed data.
            chain_id: Chain ID, sent on 8 bytes when provided.
            domain_hash: Domain hash of typed data.
            provider_message: Provider message.
            signature: Explicit signature, e.g. to send a tampered one.
        """
        if len(tx_hash) != TRANSACTION_CHECK_HASH_LENGTH:
            raise ValueError(ERR_TX_HASH_LENGTH)
        if domain_hash is not None and len(domain_hash) != TRANSACTION_CHECK_HASH_LENGTH:
            raise ValueError(ERR_DOMAIN_HASH_LENGTH)
        if partner is None and signature is None:
            raise ValueError(ERR_SIGNATURE_REQUIRED)
        self.address = address.encode() if isinstance(address, str) else address
        self.tx_hash = tx_hash
        self.risk = risk
        self.category = category
        self.tiny_url = tiny_url
        self.partner = partner
        self.simulation_type = simulation_type
        self.chain_id = chain_id
        self.domain_hash = domain_hash
        self.provider_message = provider_message
        self.signature = signature

    def serialize(self) -> bytes:
        payload = self.serialize_field(LedgerCommonFieldTag.STRUCTURE_TYPE, LedgerStructType.TYPE_TX_SIMULATION)
        payload += self.serialize_field(LedgerCommonFieldTag.VERSION, TRANSACTION_CHECK_VERSION)
        payload += self.serialize_field(TxSimulationFieldTag.SIMULATION_TYPE, self.simulation_type)
        payload += self.serialize_field(LedgerCommonFieldTag.ADDRESS, self.address)
        payload += self.serialize_field(LedgerCommonFieldTag.TX_HASH, self.tx_hash)
        payload += self.serialize_field(TxSimulationFieldTag.NORMALIZED_RISK, self.risk)
        payload += self.serialize_field(TxSimulationFieldTag.NORMALIZED_CATEGORY, self.category)
        payload += self.serialize_field(TxSimulationFieldTag.TINY_URL, self.tiny_url)
        if self.chain_id is not None:
            payload += self.serialize_field(LedgerCommonFieldTag.CHAIN_ID, self.chain_id.to_bytes(8, "big"))
        if self.domain_hash is not None:
            payload += self.serialize_field(LedgerCommonFieldTag.DOMAIN_HASH, self.domain_hash)
        if self.provider_message is not None:
            payload += self.serialize_field(TxSimulationFieldTag.PROVIDER_MESSAGE, self.provider_message)
        signature = self.signature
        if signature is None:
            if self.partner is None:
                raise ValueError(ERR_SIGNATURE_REQUIRED)
            signature = self.partner.sign(payload)
        payload += self.serialize_field(LedgerCommonFieldTag.DER_SIGNATURE, signature)
        return payload

    def get_chunks(self) -> list[bytes]:
        """Build the full list of SDK APDUs for this descriptor, ready to _exchange.

        The TLV payload is prefixed with its 2-byte big-endian total length and split over
        ``CHUNK_SIZE`` -byte chunks. P2 flags the first chunk vs continuations.
        """
        payload = self.serialize()
        payload = len(payload).to_bytes(2, "big") + payload

        apdus: list[bytes] = []
        p2 = self.P2_FIRST_CHUNK
        while payload:
            chunk = payload[: self.CHUNK_SIZE]
            apdus.append(
                bytes(
                    [
                        TRANSACTION_CHECK_CLA,
                        TRANSACTION_CHECK_INS,
                        TransactionCheckSubCommand.SUB_CMD_DESCRIPTOR,
                        p2,
                        len(chunk),
                    ]
                )
                + chunk
            )
            payload = payload[self.CHUNK_SIZE :]
            p2 = self.P2_NEXT_CHUNK
        return apdus


def get_opt_in_apdu() -> bytes:
    """Build the SDK opt-in request APDU.

    The device replies with 1 byte (enable state), after the user choice when the
    opt-in screen is displayed.
    """
    return bytes([TRANSACTION_CHECK_CLA, TRANSACTION_CHECK_INS, TransactionCheckSubCommand.SUB_CMD_OPT_IN, 0x00, 0x00])
