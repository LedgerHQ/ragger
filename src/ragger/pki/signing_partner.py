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
import hashlib
from enum import IntEnum
from pathlib import Path

from ecdsa import SigningKey
from ecdsa.util import sigencode_der

from ledgered.devices import DeviceType


class CertificatePubKeyUsage(IntEnum):
    GENUINE_CHECK = 0x01
    EXCHANGE_PAYLOAD = 0x02
    NFT_METADATA = 0x03
    TRUSTED_NAME = 0x04
    BACKUP_PROVIDER = 0x05
    RECOVER_ORCHESTRATOR = 0x06
    PLUGIN_METADATA = 0x07
    COIN_META = 0x08
    SEED_ID_AUTH = 0x09
    TX_SIMU_SIGNER = 0x0a
    CALLDATA = 0x0b
    NETWORK = 0x0c
    SWAP_TEMPLATE = 0x0d
    SAFE_ACCOUNT = 0x0e
    GATING = 0x0f


class SigningPartner:
    """A PKI signing partner that can sign payloads and onboard its certificate on a device.

    Generic over:
    - PEM key file used for signing
    - Signing algorithm (hash function + signature encoding)
    - PKI certificate APDU data per device firmware
    """

    PKI_CLA = 0xB0
    PKI_INS = 0x06

    def __init__(self,
                 pem_key_path: Path,
                 cert_pub_key_usage: CertificatePubKeyUsage,
                 certificates: dict[DeviceType, str],
                 hash_func=hashlib.sha256,
                 sigencode=sigencode_der):
        """
        Args:
            pem_key_path: Path to the PEM private key file.
            cert_pub_key_usage: PKI certificate public key usage (sent as P1 in cert APDU).
            certificates: Mapping of DeviceType -> hex-encoded certificate data string.
            hash_func: Hash function for PEM key loading and signing (default: SHA-256).
            sigencode: Signature encoding function (default: DER encoding).
        """
        self._cert_pub_key_usage = cert_pub_key_usage
        self._certificates = certificates
        self._sigencode = sigencode
        with open(pem_key_path) as f:
            self._signing_key = SigningKey.from_pem(f.read(), hash_func)

    def sign(self, data: bytes) -> bytes:
        """Sign data and return the encoded signature."""
        return self._signing_key.sign_deterministic(data, sigencode=self._sigencode)

    def get_certificate_payload(self, device_type: DeviceType) -> bytes:
        """Return the raw PKI certificate APDU bytes for the given device type.

        Raises:
            KeyError: If the device type has no certificate configured.
        """
        if device_type not in self._certificates:
            raise KeyError(f"No PKI certificate for device type '{device_type}' "
                           f"(usage {self._cert_pub_key_usage.name})")
        cert_data = bytes.fromhex(self._certificates[device_type])
        return bytes([self.PKI_CLA, self.PKI_INS, self._cert_pub_key_usage, 0x00,
                      len(cert_data)]) + cert_data
