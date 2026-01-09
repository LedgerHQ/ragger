"""
   Copyright 2022 Ledger SAS

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
from dataclasses import dataclass
from enum import IntEnum


class StatusWords(IntEnum):
    """ISO7816 Status Words for APDU responses.

    Refer to:
     - SDK https://github.com/LedgerHQ/ledger-secure-sdk/blob/master/include/status_words.h
     - https://www.eftlab.com/knowledge-base/complete-list-of-apdu-responses

    Notes:
    - The SWO codes are defined based on the ISO/IEC 7816-4 standard for smart cards.

    - 61XX and 6CXX are different.
      When a command returns 61XX, its process is normally completed,
      and it indicates the number of available bytes;
      it then expects a GET RESPONSE command with the appropriate length.
      When a command returns 6CXX, its process has been aborted,
      and it expects the command to be reissued.
      As mentioned above, 61XX indicates a normal completion,
      and 6CXX is considered as a transport error (defined in ISO7817-3).

    - Except for 63XX and 65XX, which warn that the persistent content has been changed,
      other status word should be used when the persistent content of the application is unchanged.

    - Status words 67XX, 6BXX, 6DXX, 6EXX, and 6FXX, where XX is not 0, are proprietary status words,
      as well as 9YYY, where YYY is not 000.
    """

    # 61 -- Normal processing, lower byte indicates the amount of data to be retrieved
    SWO_RESPONSE_BYTES_AVAILABLE = 0x6100

    # 62 -- Warning, the state of persistent memory is unchanged
    SWO_DATA_MAY_BE_CORRUPTED = 0x6281
    SWO_EOF_REACHED_BEFORE_LE = 0x6282
    SWO_SELECTED_FILE_INVALIDATED = 0x6283
    SWO_FILE_INVALID = 0x6284
    SWO_NO_INPUT_DATA_AVAILABLE = 0x6285

    # 63 -- Warning, the state of persistent memory is changed
    SWO_CARD_KEY_NOT_SUPPORTED = 0x6382
    SWO_READER_KEY_NOT_SUPPORTED = 0x6383
    SWO_PLAINTEXT_TRANS_NOT_SUPPORTED = 0x6384
    SWO_SECURED_TRANS_NOT_SUPPORTED = 0x6385
    SWO_VOLATILE_MEM_NOT_AVAILABLE = 0x6386
    SWO_NON_VOLATILE_MEM_NOT_AVAILABLE = 0x6387
    SWO_KEY_NUMBER_INVALID = 0x6388
    SWO_KEY_LENGTH_INCORRECT = 0x6389
    SWO_VERIFY_FAILED = 0x63C0  # lower 4-bits indicates the number of attempts left
    SWO_MORE_DATA_EXPECTED = 0x63F1

    # 64 -- Execution error, the state of persistent memory is unchanged
    SWO_EXECUTION_ERROR = 0x6400
    SWO_COMMAND_TIMEOUT = 0x6401

    # 65 -- Execution error, the state of persistent memory is changed
    SWO_MEMORY_WRITE_ERROR = 0x6501
    SWO_MEMORY_FAILURE = 0x6581

    # 66 -- Security-related issues
    SWO_SECURITY_ISSUE = 0x6600
    SWO_RECEIVE_ERROR_PARITY = 0x6601
    SWO_WRONG_CHECKSUM = 0x6602
    SWO_INCORRECT_PADDING = 0x6669

    # 67 -- Transport error. The length is incorrect
    SWO_WRONG_LENGTH = 0x6700

    # 68 -- Functions in CLA not supported
    SWO_NOT_SUPPORTED_ERROR_NO_INFO = 0x6800
    SWO_LOGICAL_CHANNEL_NOT_SUPPORTED = 0x6881
    SWO_SECURE_MESSAGING_NOT_SUPPORTED = 0x6882
    SWO_LAST_COMMAND_OF_CHAIN_EXPECTED = 0x6883
    SWO_COMMAND_CHAINING_NOT_SUPPORTED = 0x6884

    # 69 -- Command not allowed
    SWO_COMMAND_ERROR_NO_INFO = 0x6900
    SWO_COMMAND_NOT_ACCEPTED = 0x6901
    SWO_COMMAND_NOT_ALLOWED = 0x6980
    SWO_SUBCOMMAND_NOT_ALLOWED = 0x6981
    SWO_SECURITY_CONDITION_NOT_SATISFIED = 0x6982
    SWO_AUTH_METHOD_BLOCKED = 0x6983
    SWO_REFERENCED_DATA_BLOCKED = 0x6984
    SWO_CONDITIONS_NOT_SATISFIED = 0x6985
    SWO_COMMAND_NOT_ALLOWED_EF = 0x6986
    SWO_EXPECTED_SECURE_MSG_OBJ_MISSING = 0x6987
    SWO_INCORRECT_SECURE_MSG_DATA_OBJ = 0x6988
    SWO_PERMISSION_DENIED = 0x69F0
    SWO_MISSING_PRIVILEGES = 0x69F1

    # 6A -- Wrong parameters (with details)
    SWO_PARAMETER_ERROR_NO_INFO = 0x6A00
    SWO_INCORRECT_DATA = 0x6A80
    SWO_FUNCTION_NOT_SUPPORTED = 0x6A81
    SWO_FILE_NOT_FOUND = 0x6A82
    SWO_RECORD_NOT_FOUND = 0x6A83
    SWO_INSUFFICIENT_MEMORY = 0x6A84
    SWO_INCONSISTENT_TLV_STRUCT = 0x6A85
    SWO_INCORRECT_P1_P2 = 0x6A86
    SWO_WRONG_DATA_LENGTH = 0x6A87
    SWO_REFERENCED_DATA_NOT_FOUND = 0x6A88
    SWO_FILE_ALREADY_EXISTS = 0x6A89
    SWO_DF_NAME_ALREADY_EXISTS = 0x6A8A
    SWO_WRONG_PARAMETER_VALUE = 0x6AF0

    # 6B -- Wrong parameters P1-P2
    SWO_WRONG_P1_P2 = 0x6B00

    # 6C -- Wrong Le field. lower byte indicates the appropriate length
    SWO_INCORRECT_P3_LENGTH = 0x6C00

    # 6D -- The instruction code is not supported
    SWO_INVALID_INS = 0x6D00

    # 6E -- The instruction class is not supported
    SWO_INVALID_CLA = 0x6E00

    # 6F -- No precise diagnosis is given
    SWO_UNKNOWN = 0x6F00

    # 9- --
    SWO_SUCCESS = 0x9000
    SWO_BUSY = 0x9001
    SWO_PIN_NOT_SUCCESFULLY_VERIFIED = 0x9004
    SWO_RESULT_OK = 0x9100
    SWO_STATES_STATUS_WRONG = 0x9101
    SWO_TRANSACTION_LIMIT_REACHED = 0x9102
    SWO_INSUFFICIENT_MEM_FOR_CMD = 0x910E
    SWO_COMMAND_CODE_NOT_SUPPORTED = 0x911C
    SWO_INVALID_KEY_NUMBER = 0x9140
    SWO_WRONG_LENGTH_FOR_INS = 0x917E
    SWO_NO_EF_SELECTED = 0x9400
    SWO_ADDRESS_RANGE_EXCEEDED = 0x9402
    SWO_FID_NOT_FOUND = 0x9404
    SWO_PARSE_ERROR = 0x9405
    SWO_NO_PIN_DEFINED = 0x9802
    SWO_ACCESS_CONDITION_NOT_FULFILLED = 0x9804


@dataclass
class ExceptionRAPDU(Exception):
    """
    Depending on the :class:`RaisePolicy <ragger.backend.interface.RaisePolicy>`,
    communication with an application can raise this exception.

    Just like :class:`RAPDU <ragger.utils.structs.RAPDU>`, it is composed of two
    attributes:

    - ``status`` (``int``), which is extracted from the two last bytes of the
      response,
    - ``data`` (``bytes``), which is the entire response payload, except the two
      last bytes.
    """

    status: int
    data: bytes = bytes()

    def __str__(self):
        return f"Error [0x{self.status:x}] {str(self.data)}"


class MissingElfError(Exception):
    """Exception raised when an expected ELF binary is missing."""

    def __init__(self, path: str):
        super().__init__(f"File '{path}' missing. Did you compile for this target?")
        self.path = path
