from unittest import TestCase

from ragger.error import ExceptionRAPDU


class TestExceptionRAPDU(TestCase):

    def test___str__(self):
        status, name, data = 99, 'name', b"data"
        error = ExceptionRAPDU(status, name, data)
        for word in [f"0x{status:x}", name, str(data)]:
            self.assertIn(word, str(error))
