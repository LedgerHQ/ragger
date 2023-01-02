from unittest import TestCase

from ragger.error import ExceptionRAPDU


class TestExceptionRAPDU(TestCase):

    def test___str__(self):
        status, data = 99, b"data"
        error = ExceptionRAPDU(status, data)
        for word in [f"0x{status:x}", str(data)]:
            self.assertIn(word, str(error))
