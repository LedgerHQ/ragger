from ledgered.devices import Devices, DeviceType
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from ragger.backend import SpeculosBackend
from ragger.navigator import NavInsID, NavIns, NanoNavigator

from tests.stubs import SpeculosServerStub

ROOT_SCREENSHOT_PATH = Path(__file__).parent.parent.parent.resolve()


class TestNavigator(TestCase):
    """
    Test patterns explained:

    ```
    def test_something(self):
        # patches 'subprocess' so that Speculos Client won't actually launch an app inside Speculos
        with patch("speculos.client.subprocess"):
            # starts the Speculos server stub, which will answer the SpeculosClient requests
            with SpeculosServerStub():
                # starts the backend: starts the underlying SpeculosClient so that exchanges can be
                # performed
                with self.backend:
    ```

    Sent APDUs:

    - starting with '00' means the response has a APDUStatus.SUCCESS status (0x9000)
    - else means the response has a APDUStatus.ERROR status (arbitrarily set to 0x8000)
    """

    def setUp(self):
        self.device = Devices.get_by_type(DeviceType.NANOS)
        self.backend = SpeculosBackend("some app", self.device)
        self.navigator = NanoNavigator(self.backend, self.device)

    def test_navigate_and_compare(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    instructions = [
                        NavIns(NavInsID.RIGHT_CLICK),
                        NavIns(NavInsID.RIGHT_CLICK),
                        NavIns(NavInsID.LEFT_CLICK),
                        NavIns(NavInsID.RIGHT_CLICK),
                        NavIns(NavInsID.BOTH_CLICK),
                        NavIns(NavInsID.RIGHT_CLICK),
                        NavIns(NavInsID.BOTH_CLICK),
                        NavIns(NavInsID.WAIT, (2, ))
                    ]
                    self.navigator.navigate_and_compare(
                        ROOT_SCREENSHOT_PATH,
                        "test_navigate_and_compare",
                        instructions,
                        screen_change_before_first_instruction=False,
                        screen_change_after_last_instruction=False)

    def test_navigate_and_compare_no_golden(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    instructions = [NavIns(NavInsID.RIGHT_CLICK)]
                    with self.assertRaises(FileNotFoundError) as error:
                        self.navigator.navigate_and_compare(
                            ROOT_SCREENSHOT_PATH,
                            "test_navigate_and_compare_no_golden",
                            instructions,
                            screen_change_before_first_instruction=False)
                    self.assertIn("No such file or directory", str(error.exception))
                    self.assertIn("test_navigate_and_compare_no_golden/00001.png",
                                  str(error.exception))

    def test_navigate_and_compare_wrong_golden(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    instructions = [NavIns(NavInsID.RIGHT_CLICK)]
                    with self.assertRaises(AssertionError) as error:
                        self.navigator.navigate_and_compare(
                            ROOT_SCREENSHOT_PATH,
                            "test_navigate_and_compare_wrong_golden",
                            instructions,
                            screen_change_before_first_instruction=False)
                    self.assertIn("Screen does not match golden", str(error.exception))
                    self.assertIn("00001.png", str(error.exception))

    def test_navigate_until_snap(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    ret = self.navigator.navigate_until_snap(NavIns(NavInsID.RIGHT_CLICK),
                                                             NavIns(NavInsID.BOTH_CLICK),
                                                             ROOT_SCREENSHOT_PATH, "generic",
                                                             "00000.png", "00002.png")
                self.assertEqual(ret, 2)

    def test_navigate_fail_cannot_find_first_snap(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    with self.assertRaises(ValueError) as error:
                        self.navigator.navigate_until_snap(NavIns(NavInsID.RIGHT_CLICK),
                                                           NavIns(NavInsID.BOTH_CLICK),
                                                           ROOT_SCREENSHOT_PATH, "generic",
                                                           "00003.png", "00002.png")
                    self.assertIn("Could not find first snapshot", str(error.exception))

    def test_navigate_fail_cannot_find_last_snap(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    with self.assertRaises(TimeoutError) as error:
                        self.navigator.navigate_until_snap(NavIns(NavInsID.RIGHT_CLICK),
                                                           NavIns(NavInsID.BOTH_CLICK),
                                                           ROOT_SCREENSHOT_PATH,
                                                           "generic",
                                                           "00000.png",
                                                           "00004.png",
                                                           timeout=5)
                    self.assertIn("Timeout waiting for snap", str(error.exception))

    def test_navigate_until_text(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    self.navigator.navigate_until_text(NavIns(NavInsID.RIGHT_CLICK),
                                                       [NavIns(NavInsID.BOTH_CLICK)],
                                                       "About",
                                                       screen_change_before_first_instruction=False)

    def test_navigate_until_text_screen_change_timeout(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    with self.assertRaises(TimeoutError) as error:
                        self.navigator.navigate_until_text(
                            NavIns(NavInsID.BOTH_CLICK), [NavIns(NavInsID.BOTH_CLICK)],
                            "WILL NOT BE FOUND",
                            timeout=5,
                            screen_change_before_first_instruction=False)
                    self.assertIn("Timeout waiting for screen change", str(error.exception))

    def test_navigate_until_text_and_compare(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    self.navigator.navigate_until_text_and_compare(
                        NavIns(NavInsID.RIGHT_CLICK), [NavIns(NavInsID.BOTH_CLICK)],
                        "About",
                        ROOT_SCREENSHOT_PATH,
                        "test_navigate_until_text_and_compare",
                        screen_change_before_first_instruction=False)

    def test_navigate_until_text_and_compare_no_golden(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    with self.assertRaises(FileNotFoundError) as error:
                        self.navigator.navigate_until_text_and_compare(
                            NavIns(NavInsID.RIGHT_CLICK), [NavIns(NavInsID.BOTH_CLICK)],
                            "About",
                            ROOT_SCREENSHOT_PATH,
                            "test_navigate_and_compare_no_golden",
                            screen_change_before_first_instruction=False)
                    self.assertIn("No such file or directory", str(error.exception))
                    self.assertIn("test_navigate_and_compare_no_golden/00001.png",
                                  str(error.exception))

    def test_navigate_until_text_and_compare_wrong_golden(self):
        with patch("speculos.client.subprocess"):
            with SpeculosServerStub():
                with self.backend:
                    with self.assertRaises(AssertionError) as error:
                        self.navigator.navigate_until_text_and_compare(
                            NavIns(NavInsID.RIGHT_CLICK), [NavIns(NavInsID.BOTH_CLICK)],
                            "About",
                            ROOT_SCREENSHOT_PATH,
                            "test_navigate_and_compare_wrong_golden",
                            screen_change_before_first_instruction=False)
                    self.assertIn("Screen does not match golden", str(error.exception))
                    self.assertIn("00001.png", str(error.exception))
