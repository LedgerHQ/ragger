from io import BytesIO
from ledgered.devices import DeviceType, Devices
from typing import List
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ragger.backend import SpeculosBackend

APPNAME = "some app"


def get_next_in_list(the_list: List, elt: str) -> str:
    index = the_list.index(elt)
    return the_list[index + 1]


class TestSpeculosBackend(TestCase):

    maxDiff = None

    def setUp(self):
        self.nanos = Devices.get_by_type(DeviceType.NANOS)

    def test___init__ok(self):
        b = SpeculosBackend(APPNAME, self.nanos)
        self.assertEqual(b._api_port, b._DEFAULT_API_PORT)
        self.assertEqual(b._apdu_port, b._DEFAULT_API_PORT + 1)

    def test___init__ports_ok(self):
        api_port, apdu_port = 4567, 9876
        b1 = SpeculosBackend(APPNAME,
                             self.nanos,
                             args=["--api-port",
                                   str(api_port), "--apdu-port",
                                   str(apdu_port)])
        self.assertEqual(b1._api_port, api_port)
        self.assertEqual(b1._apdu_port, apdu_port)

        b2 = SpeculosBackend(APPNAME, self.nanos, args=["--api-port", str(api_port)])
        self.assertEqual(b2._api_port, api_port)
        self.assertEqual(b2._apdu_port, api_port + 1)

        b3 = SpeculosBackend(APPNAME, self.nanos, args=["--apdu-port", str(apdu_port)])
        self.assertEqual(b3._api_port, b3._DEFAULT_API_PORT)
        self.assertEqual(b3._apdu_port, apdu_port)

    def test___init__args_ok(self):
        SpeculosBackend(APPNAME, self.nanos, args=["some", "specific", "arguments"])

    def test___init__args_nok(self):
        with self.assertRaises(AssertionError):
            SpeculosBackend(APPNAME, self.nanos, args="not a list")

    def test_context_manager(self):
        expected_image = b"1234"
        with patch("ragger.backend.speculos.SpeculosClient"):
            backend = SpeculosBackend(APPNAME, self.nanos)
        self.assertIsNone(backend._last_screenshot)
        self.assertIsNone(backend._home_screenshot)
        # patching SpeculosClient.get_screenshot
        backend._client.get_screenshot.return_value = expected_image
        # patching method so that __enter__ is not stuck for 20s
        backend._retrieve_client_screen_content = lambda: {"events": True}
        with backend as yielded:
            self.assertTrue(backend._client.__enter__.called)
            self.assertEqual(backend, yielded)
            self.assertEqual(backend._last_screenshot, backend._home_screenshot)
            self.assertEqual(backend._last_screenshot.getvalue(),
                             BytesIO(expected_image).getvalue())
            self.assertFalse(backend._client.__exit__.called)
        self.assertTrue(backend._client.__exit__.called)

    def test_batch_ok(self):
        with patch("ragger.backend.speculos.SpeculosClient") as patched_client:
            client_number = 2
            arg_api_port = 1234
            arg_apdu_port = 4321

            clients = SpeculosBackend.batch(
                APPNAME,
                self.nanos,
                client_number,
                different_attestation=True,
                args=['--apdu-port', arg_apdu_port, '--api-port', arg_api_port])

            self.assertEqual(len(clients), client_number)
            self.assertEqual(patched_client.call_count, client_number)
            all_client_args = patched_client.call_args_list

            client_seeds = set()
            client_rngs = set()
            client_priv_keys = set()
            client_attestations = set()
            client_api_ports = set()
            client_apdu_ports = set()

            for index, client in enumerate(clients):
                args, kwargs = all_client_args[index]
                self.assertEqual(args, ())
                self.assertEqual(kwargs["app"], APPNAME)
                self.assertEqual(kwargs["api_url"], f"http://127.0.0.1:{client._api_port}")
                speculos_args = kwargs["args"]
                client_seeds.add(get_next_in_list(speculos_args, "--seed"))
                client_rngs.add(get_next_in_list(speculos_args, "--deterministic-rng"))
                client_priv_keys.add(get_next_in_list(speculos_args, "--user-private-key"))
                client_attestations.add(get_next_in_list(speculos_args, "--attestation-key"))
                api_port = int(get_next_in_list(speculos_args, "--api-port"))
                client_api_ports.add(client._api_port)
                apdu_port = int(get_next_in_list(speculos_args, "--apdu-port"))
                client_apdu_ports.add(client._api_port)

                # ports given as original arguments are overridden
                self.assertNotEqual(api_port, arg_api_port)
                self.assertNotEqual(apdu_port, arg_api_port)
                # API port has been overridden by a generated port
                # (APDU port too, but it is not stored into SpeculosBackend)
                self.assertEqual(client._api_port, api_port)

                self.assertIsInstance(client, SpeculosBackend)
                self.assertIsInstance(client._client, MagicMock)

            # all API ports are different
            self.assertEqual(len(client_api_ports), client_number)
            # all APDU ports are different
            self.assertEqual(len(client_apdu_ports), client_number)
            # all seeds ports are different
            self.assertEqual(len(client_seeds), client_number)
            # all RNGs are different
            self.assertEqual(len(client_rngs), client_number)
            # all private keys are different
            self.assertEqual(len(client_priv_keys), client_number)
            # all attestations are different
            self.assertEqual(len(client_attestations), client_number)
