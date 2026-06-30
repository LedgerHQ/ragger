from unittest import TestCase

from ragger.tlv import TlvSerializable, der_encode, format_tlv


class TestDerEncode(TestCase):
    def test_single_byte_below_0x80(self):
        self.assertEqual(b"\x00", der_encode(0))
        self.assertEqual(b"\x01", der_encode(1))
        self.assertEqual(b"\x7f", der_encode(0x7F))

    def test_long_form_at_and_above_0x80(self):
        # 0x80 needs the long form: 0x81 (one extra byte) + 0x80
        self.assertEqual(b"\x81\x80", der_encode(0x80))
        self.assertEqual(b"\x81\xff", der_encode(0xFF))
        # two value bytes -> 0x82 prefix
        self.assertEqual(b"\x82\x01\x00", der_encode(0x100))
        self.assertEqual(b"\x82\x3f\xff", der_encode(0x3FFF))


class TestFormatTlv(TestCase):
    def test_int_value_minimal_big_endian(self):
        self.assertEqual(b"\x01\x01\x01", format_tlv(0x01, 1))
        # an 8-byte chain id encoded with its minimal length
        self.assertEqual(
            b"\x23\x05\x12\x34\x56\x78\x90",
            format_tlv(0x23, 0x1234567890),
        )

    def test_str_value_is_utf8(self):
        self.assertEqual(b"\x20\x02AB", format_tlv(0x20, "AB"))

    def test_bytes_and_bytearray_value(self):
        self.assertEqual(b"\x22\x03abc", format_tlv(0x22, b"abc"))
        self.assertEqual(b"\x22\x03abc", format_tlv(0x22, bytearray(b"abc")))

    def test_tag_above_0x80_is_der_encoded(self):
        # tag 0xf0 -> 0x81 0xf0, length 1, value 'x'
        self.assertEqual(b"\x81\xf0\x01x", format_tlv(0xF0, b"x"))

    def test_length_above_0x80_is_der_encoded(self):
        value = b"A" * 200
        self.assertEqual(b"\x20\x81\xc8" + value, format_tlv(0x20, value))

    def test_empty_value(self):
        self.assertEqual(b"\x20\x00", format_tlv(0x20, b""))

    def test_unhandled_type_raises(self):
        with self.assertRaises(AssertionError):
            format_tlv(0x20, 1.5)  # type: ignore[arg-type]


class TestTlvSerializable(TestCase):
    def test_serialize_is_abstract(self):
        with self.assertRaises(NotImplementedError):
            TlvSerializable().serialize()

    def test_static_helpers_delegate_to_module_functions(self):
        self.assertEqual(der_encode(0x80), TlvSerializable.der_encode(0x80))
        self.assertEqual(
            format_tlv(0x20, "AB"), TlvSerializable.serialize_field(0x20, "AB")
        )

    def test_subclass_can_build_a_payload(self):

        class Sample(TlvSerializable):
            def serialize(self) -> bytes:
                return self.serialize_field(0x01, 1) + self.serialize_field(0x20, "AB")

        self.assertEqual(b"\x01\x01\x01\x20\x02AB", Sample().serialize())
