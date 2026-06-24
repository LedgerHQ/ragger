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
from typing import Union


def der_encode(value: int) -> bytes:
    """DER-encode an unsigned integer (used for both TLV tags and lengths).

    Values below 0x80 are encoded as a single byte. Larger values are encoded as
    a length-prefix byte (0x80 | byte_count) followed by the big-endian bytes.
    """
    # max() to have a minimum length of 1
    value_bytes = value.to_bytes(max(1, (value.bit_length() + 7) // 8), 'big')
    if value >= 0x80:
        value_bytes = (0x80 | len(value_bytes)).to_bytes(1, 'big') + value_bytes
    return value_bytes


def format_tlv(tag: int, value: Union[int, str, bytes, bytearray]) -> bytes:
    """Serialize a single (tag, value) pair into a DER-style TLV triplet.

    ``int`` values are encoded as minimal-length big-endian bytes and ``str``
    values as their UTF-8 encoding before the length/value are emitted.
    """
    if isinstance(value, int):
        # max() to have a minimum length of 1
        value = value.to_bytes(max(1, (value.bit_length() + 7) // 8), 'big')
    elif isinstance(value, str):
        value = value.encode()
    elif isinstance(value, bytearray):
        value = bytes(value)

    assert isinstance(value, bytes), f"Unhandled TLV formatting for type : {type(value)}"

    tlv = bytearray()
    tlv += der_encode(tag)
    tlv += der_encode(len(value))
    tlv += value
    return bytes(tlv)


class TlvSerializable:
    """Base class for objects that serialize themselves into a TLV payload.

    Subclasses implement :meth:`serialize`, concatenating one :meth:`serialize_field`
    (a.k.a. :func:`format_tlv`) per field. This is transport-agnostic: APDU framing
    (CLA/INS, chunking) is the caller's responsibility.
    """

    def serialize(self) -> bytes:
        raise NotImplementedError

    @staticmethod
    def der_encode(value: int) -> bytes:
        return der_encode(value)

    @staticmethod
    def serialize_field(tag: int, value: Union[int, str, bytes, bytearray]) -> bytes:
        return format_tlv(tag, value)
