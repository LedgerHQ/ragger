from unittest import TestCase

from ragger.utils import structs


class TestStructsRAPDU(TestCase):

    def test___str__data(self):
        status = 19
        data = "012345"
        rapdu = structs.RAPDU(status, bytes.fromhex(data))
        self.assertEqual(f"[0x{status:x}] " + data, str(rapdu))

    def test___str__no_data(self):
        status = 19
        rapdu = structs.RAPDU(status, None)
        self.assertEqual(f"[0x{status:x}] <Nothing>", str(rapdu))
