from unittest import TestCase
from typing import Tuple
# from ragger.bip.seed import Seed
from ragger.bip import calculate_public_key_and_chaincode, CurveChoice
from bip_utils import Bip32KeyError

# Disable yapf as it proposes unreadable test vectors
# yapf: disable


class TestSeed(TestCase):

    def _assert_return(self,
                       path: str,
                       ref_public_key: str,
                       ref_comp_public_key: str,
                       ref_chaincode: str,
                       curve: CurveChoice):
        public_key, chaincode = calculate_public_key_and_chaincode(curve=curve, path=path)
        self.assertEqual(public_key, ref_public_key)
        self.assertEqual(chaincode, ref_chaincode)

        comp_public_key, chaincode = calculate_public_key_and_chaincode(curve=curve,
                                                                        path=path,
                                                                        compress_public_key=True)
        self.assertEqual(comp_public_key, ref_comp_public_key)
        self.assertEqual(chaincode, ref_chaincode)

    def test_get_public_key_and_chaincode_error_curve(self):
        with self.assertRaises(ValueError):
            calculate_public_key_and_chaincode(0, path="m/0'/0'/0'/0/0")

    def test_get_public_key_and_chaincode_error_unhardened_path(self):
        with self.assertRaises(Bip32KeyError):
            calculate_public_key_and_chaincode(curve=CurveChoice.Ed25519Slip,
                                               path="m/44'/601/1430/20/0/0")
        with self.assertRaises(Bip32KeyError):
            calculate_public_key_and_chaincode(curve=CurveChoice.Ed25519Blake2bSlip,
                                               path="m/44'/601/1430/20/0/0")

    def test_get_public_key_and_chaincode_secp256k1(self):
        secp256k1_test_values: Tuple[Tuple[str, str, str]] = (
            ("m/44'/0'",
             "049cf864c874c05959780f5c80e20f837b5f304367bde75508ceba499e54f0ef7c848279d96aa18e50cf09494c7adba9a6f166d2d92952892f18ece854c919159d",
             "039cf864c874c05959780f5c80e20f837b5f304367bde75508ceba499e54f0ef7c",
             "a4b1681a60ae4a858f68632a6da5a95ae128d4c4891672de5f0d13a9141e3a08"),
            ("m/44'/0'/0'/0/0",
             "044251358da206b3d549f5c538a7bc466427ee81099aa8b40dd0f5d4bfac5f5f152ea7968164873f9f7a9430d3eab432ae8d2484b513e5b3bd2d0b8d6a0251314b",
             "034251358da206b3d549f5c538a7bc466427ee81099aa8b40dd0f5d4bfac5f5f15",
             "7bdcc51250dde2fe6372e1d5c810b08684e506615223db183cb8096637f77d2f"),
            ("m/44'/601'/1430'/20'/0'/0'",
             "04202f3dc031c95de188189d969d4aa5cb2206e34487de132f2cb0998e11f0738edf71a945b077de2c1ea21cc3d4484a02597f7e8e20cf7af9cf1decc5b225c63d",
             "03202f3dc031c95de188189d969d4aa5cb2206e34487de132f2cb0998e11f0738e",
             "13b9df5169e7c40ddff549003ee390444178db9af8ee08534b0c6700573cc8fc"),
            ("m/44'/601/1430/20/0/0",
             "04b07eb50072f60f634319b86158ad2e367622014767374674fbd56097c62e4a6b36ae453d7f1eb1635f61a70dcb6333a7963bbee4b5295f748dcbfc63e71d7fe2",
             "02b07eb50072f60f634319b86158ad2e367622014767374674fbd56097c62e4a6b",
             "94267cd146456f0aeb53459380075ea16583f3791542b3eaedce7f3c04e6bd0f"),
        )
        for refs in secp256k1_test_values:
            self._assert_return(*refs, CurveChoice.Secp256k1)

    def test_get_public_key_and_chaincode_nist256p1(self):
        nist256p1_test_values: Tuple[Tuple[str, str, str]] = (
            ("m/44'/0'",
             "04cc70e8a1d99dd7dfa962e22f236d1be2f033714644a4c3515c64b8b9ba63e56b95ce3053c98733b5c0cc1e376ead8fed94cc78b0b2bf1bca5e12135ea864c8b8",
             "02cc70e8a1d99dd7dfa962e22f236d1be2f033714644a4c3515c64b8b9ba63e56b",
             "0aca88bf7725c7a2848f469d4d75f892f121d52307f63727968f5db1c68f06aa"),
            ("m/44'/0'/0'/0/0",
             "0448c284314849a6034315dd58362891b8a10e3d63b60d1409f3be4736b7dce740aaa16cd05df874f3b1dd291293b0a01dd2aa851db6c6143366ecc78a82db24ac",
             "0248c284314849a6034315dd58362891b8a10e3d63b60d1409f3be4736b7dce740",
             "d8d006dc8199b09aacd77494db7803eb17ce090c9f018c1dfd80dcf44353a98a"),
            ("m/44'/601'/1430'/20'/0'/0'",
             "047f3ff931a503774d82fd01c8a6eab20abb45395ca76872aa65ed06828b355a285b2a73fe0dcb63efa0f75f943460e335bb01920c412a63caae17898ab9d84bd2",
             "027f3ff931a503774d82fd01c8a6eab20abb45395ca76872aa65ed06828b355a28",
             "c8f697a463fcb0c52a5220766f7b58f503d14b2c79e37a82320e17b9bb5bc741"),
            ("m/44'/601/1430/20/0/0",
             "0457ba6d8ab14a9184dbcf9a3fb32d8cf1011cc68f4883955e22f51c9167424822493182a6c6a19cf88437b426ab6f96c2e557a0ff68f6c19a01ad9c2562660624",
             "0257ba6d8ab14a9184dbcf9a3fb32d8cf1011cc68f4883955e22f51c9167424822",
             "45e506e3dc52bdd0752d035bd0262f3c518bcd1a2f4e9fdaf1201f4dc26541c3"),
        )
        for refs in nist256p1_test_values:
            self._assert_return(*refs, CurveChoice.Nist256p1)

    def test_get_public_key_and_chaincode_ed25519slip(self):
        ed25519slip_test_values: Tuple[Tuple[str, str, str]] = (
            ("m/44'/0'",
             "00878ee3e0514e12dbbfa81a46f5bfea2e2266fef56e6e2fac64cac2d244a1b1bf",
             "00878ee3e0514e12dbbfa81a46f5bfea2e2266fef56e6e2fac64cac2d244a1b1bf",
             "4103e5fb91a143a23db9a210e698c196d146f7e7cad678d598bacf80efe7e28d"),
            ("m/44'/0'/0'/0'/0'",
             "00c2ea5e68ab428901e21cb1370765b4cff3abea905d4b4b2efebf977c6202782a",
             "00c2ea5e68ab428901e21cb1370765b4cff3abea905d4b4b2efebf977c6202782a",
             "b40ac81f3f3a3edc493edc95fcb2a7b1735aa2a5a706f0ee4511c3d0f5dfaf06"),
            ("m/44'/601'/1430'/20'/0'/0'",
             "0059e258339ae430ded97912ed077038edf189ceb8f7d022741a9000950b131f30",
             "0059e258339ae430ded97912ed077038edf189ceb8f7d022741a9000950b131f30",
             "a6e90bed1450e77a6f3933b075fa23be315e676ccd5eddd778a62e3d669ab2d6"),
        )
        for refs in ed25519slip_test_values:
            self._assert_return(*refs, CurveChoice.Ed25519Slip)

    def test_get_public_key_and_chaincode_ed25519kholaw(self):
        ed25519kholaw_test_values: Tuple[Tuple[str, str, str]] = (
            ("m/44'/0'",
             "003108582f9d96e765606f34a7bcc0519e0de48440f91672b205ce8e4cb17d6f14",
             "003108582f9d96e765606f34a7bcc0519e0de48440f91672b205ce8e4cb17d6f14",
             "cd2d6a86d12dd802f5e63417b7dba105b44f4abc97ae3038da8de17e605d6062"),
            ("m/44'/0'/0'/0/0",
             "00ea217a126a470fabe7d37eb15ad9def9e6f37cf99f3692bbecd35fc81456d966",
             "00ea217a126a470fabe7d37eb15ad9def9e6f37cf99f3692bbecd35fc81456d966",
             "506f2b675c814014feb015f747359f5e63cba57fdb03bc76c0e56dd9e945db44"),
            ("m/44'/601'/1430'/20'/0'/0'",
             "001875702d0ac409adc95f83c3291dddc71c2fb39540805762d4410596da88ad64",
             "001875702d0ac409adc95f83c3291dddc71c2fb39540805762d4410596da88ad64",
             "9071b11878fdcfbf1fd9aaa8522fe7d5ec0427823917ce97becb5f93b351eebb"),
            ("m/44'/601/1430/20/0/0",
             "00054b1cf268385d39f6b40e606c0358782f25600811abd01f765ace92efae4ab1",
             "00054b1cf268385d39f6b40e606c0358782f25600811abd01f765ace92efae4ab1",
             "8bcadebd6683fd232e781c31ac1a150cf48e89bd9e3dbe58a144d15919f92746"),
        )
        for refs in ed25519kholaw_test_values:
            self._assert_return(*refs, CurveChoice.Ed25519Kholaw)

    def test_get_public_key_and_chaincode_ed25519blake2bslip(self):
        ed25519blake2bslip_test_values: Tuple[Tuple[str, str, str]] = (
            ("m/44'/0'",
             "00a22f09fde3338341f2be204121c935d32be753a0eec22f1746ee9db07670bce6",
             "00a22f09fde3338341f2be204121c935d32be753a0eec22f1746ee9db07670bce6",
             "4103e5fb91a143a23db9a210e698c196d146f7e7cad678d598bacf80efe7e28d"),
            ("m/44'/0'/0'/0'/0'",
             "004f84a21e5c4f2dc8a5e394d2a7d301dad3dd55b0f1c1c016ca461e9b693bd801",
             "004f84a21e5c4f2dc8a5e394d2a7d301dad3dd55b0f1c1c016ca461e9b693bd801",
             "b40ac81f3f3a3edc493edc95fcb2a7b1735aa2a5a706f0ee4511c3d0f5dfaf06"),
            ("m/44'/601'/1430'/20'/0'/0'",
             "0055c33d890e75ef38258bb2e77031d6bc49507d53ca2772ef0ec9eae5242f05a7",
             "0055c33d890e75ef38258bb2e77031d6bc49507d53ca2772ef0ec9eae5242f05a7",
             "a6e90bed1450e77a6f3933b075fa23be315e676ccd5eddd778a62e3d669ab2d6"),
        )
        for refs in ed25519blake2bslip_test_values:
            self._assert_return(*refs, CurveChoice.Ed25519Blake2bSlip)
