from unittest import TestCase

from ragger.bip.seed import Seed


class TestSeed(TestCase):

    def setUp(self):
        self.mnemonic = "glory promote mansion idle axis finger extra february uncover one trip " \
            "resource lawn turtle enact monster seven myth punch hobby comfort wild raise skin"
        self.seed = Seed.from_mnemonic(self.mnemonic)

    def test_get_pubkey(self):
        path_to_key = (
            # BTC: 44'/0'/0'/0/0
            ("8000002c 80000000 80000000 00000000 00000000",
             "044251358da206b3d549f5c538a7bc466427ee81099aa8b40dd0f5d4bfac5f5f1"
             "52ea7968164873f9f7a9430d3eab432ae8d2484b513e5b3bd2d0b8d6a0251314b"),
            # ETH: 44'/60'/0'/0/0
            ("8000002c 8000003c 80000000 00000000 00000000",
             "04ef5b152e3f15eb0c50c9916161c2309e54bd87b9adce722d69716bcdef85f54"
             "7678e15ab40a78919c7284e67a17ee9a96e8b9886b60f767d93023bac8dbc16e4"),
            # LTC: 49'/2'/0'/0/0
            ("80000031 80000002 80000000 00000000 00000000",
             "047503e09409149c042c76020da3425bbea35eaeeaaf0f6b438dcc8e3820d9a41"
             "c2e14029a47f0c63fa6913f5f9c326d1e78607346261b2a3abff3b829d7dacb39"))
        for path, key in path_to_key:
            self.assertEqual(self.seed.get_pubkey(bytes.fromhex(path)), bytes.fromhex(key))

    def test_get_pubkey_error_path_too_short(self):
        with self.assertRaises(ValueError) as error:
            self.seed.get_pubkey(bytes.fromhex("8000002c"))
        self.assertIn("too short", str(error.exception))

    def test_get_pubkey_error_unknwon_purpose(self):
        with self.assertRaises(ValueError) as error:
            self.seed.get_pubkey(bytes.fromhex("800000ff 80000000"))
        self.assertIn("Purpose", str(error.exception))

    def test_get_pubkey_error_unknwon_change(self):
        with self.assertRaises(ValueError) as error:
            self.seed.get_pubkey(bytes.fromhex("8000002c 80000000 80000000 000000ff"))
        self.assertIn("Change", str(error.exception))

    def test_get_address_bitcoin(self):
        # BTC: 44'/0'/0'/0/0
        path = bytes.fromhex("8000002c 80000000 80000000 00000000 00000000")
        addr_formats = {
            "p2pkh": "1KKLP5MNa9mmWnEziT5skyu7PZ8A4eFisB",
            "p2sh": "3HDL3XF7bRmWFSmwF6Z74edjWw1vFv1Y5q",
            "bech32": "bc1qer57ma0fzhqys2cmydhuj9cprf9eg0nw922a8j"
        }
        for fmt, expected in addr_formats.items():
            self.assertEqual(self.seed.get_address(path, encoding=fmt), expected)

    def test_get_address_bitcoin_testnet(self):
        # BTC TESTNET: 44'/1'/0'/0/0
        path = bytes.fromhex("8000002c 80000001 80000000 00000000 00000000")
        addr_formats = {
            "p2pkh": "myqHg8SMPBD2HticS24Fau7SFYirvzkABD",
            "p2sh": "2N8mY7GB9CtGrTEQUvEAygbczjHE64wPK2x",
            "bech32": "tb1qer57ma0fzhqys2cmydhuj9cprf9eg0nw0v3wup"
        }
        for fmt, expected in addr_formats.items():
            self.assertEqual(self.seed.get_address(path, encoding=fmt), expected)

    def test_get_address_litecoin(self):
        # LTC: 44'/2'/0'/0/0
        path = bytes.fromhex("8000002c 80000002 80000000 00000000 00000000")
        addr_formats = {
            "p2pkh": "LbSAY7xS2BB78yDx97z7L3PmqDVgAkNnRh",
            "p2sh": "MQ4hJE4K7bvCT48UWHZ2y38xpM127PyBMz",
            "bech32": "ltc1qk8g5qzzm063lt67yd4ya40kceduw03pyeum2cl"
        }
        for fmt, expected in addr_formats.items():
            self.assertEqual(self.seed.get_address(path, encoding=fmt), expected)

        path = bytes.fromhex("80000031 80000002 80000000 00000000 00000000")
        self.assertEqual(self.seed.get_address(path, encoding="p2sh"),
                         "MJovkMvQ2rXXUj7TGVvnQyVMWghSdqZsmu")

    def test_get_address_ethereum(self):
        # ETH: 44'/60'/0'/0/0
        path = bytes.fromhex("8000002c 8000003c 80000000 00000000 00000000")
        expected = "0xDad77910DbDFdE764fC21FCD4E74D71bBACA6D8D"
        self.assertEqual(self.seed.get_address(path), expected)

    def test_get_address_unknown_encoder_fallback_default(self):
        # LTC: 44'/2'/0'/0/0
        path = bytes.fromhex("8000002c 80000002 80000000 00000000 00000000")
        encoder = "not existing"
        self.assertEqual(self.seed.get_address(path, encoding=encoder), self.seed.get_address(path))
