from io import StringIO
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ledgered.devices import Devices, DeviceType

from ragger.navigator import ManualNavigator, NavIns, NavInsID


class TestManualNavigator(TestCase):
    def setUp(self):
        self.backend = MagicMock()
        self.device = Devices.get_by_type(DeviceType.FLEX)
        self.navigator = ManualNavigator(self.backend, self.device)

    def _patch_tty(self):
        tty = MagicMock(wraps=StringIO("\n"))
        tty.__enter__.return_value = tty
        return patch.object(ManualNavigator, "_open_tty", return_value=tty), tty

    def test_navigate_async_pending_returns_immediately(self):
        self.backend.is_async_exchange_pending = True
        patcher, _ = self._patch_tty()
        with patcher as open_tty:
            self.navigator.navigate([NavInsID.USE_CASE_CHOICE_CONFIRM])
            self.navigator.navigate_until_text(NavInsID.SWIPE_CENTER_TO_LEFT, [NavInsID.USE_CASE_REVIEW_CONFIRM], "Hold")
        open_tty.assert_not_called()
        self.backend.finger_touch.assert_not_called()

    def test_navigate_waits_for_user(self):
        self.backend.is_async_exchange_pending = False
        patcher, tty = self._patch_tty()
        with patcher as open_tty:
            self.navigator.navigate([NavIns(NavInsID.TOUCH, (200, 300)), NavInsID.USE_CASE_SETTINGS_NEXT])
        open_tty.assert_called_once()
        written = "".join(c.args[0] for c in tty.write.call_args_list)
        self.assertIn("TOUCH(200, 300), USE_CASE_SETTINGS_NEXT", written)
        tty.readline.assert_called_once()
        self.backend.finger_touch.assert_not_called()

    def test_navigate_until_snap_waits_for_user(self):
        self.backend.is_async_exchange_pending = False
        patcher, tty = self._patch_tty()
        with patcher:
            idx = self.navigator.navigate_until_snap(
                NavInsID.SWIPE_CENTER_TO_LEFT, NavInsID.USE_CASE_REVIEW_CONFIRM, MagicMock(), "test", "00000", "00003"
            )
        self.assertEqual(idx, 0)
        tty.readline.assert_called_once()

    def test_navigate_without_tty_uses_input(self):
        self.backend.is_async_exchange_pending = False
        with patch.object(ManualNavigator, "_open_tty", return_value=None), patch("builtins.input") as mock_input:
            self.navigator.navigate([NavInsID.USE_CASE_CHOICE_CONFIRM])
        mock_input.assert_called_once()
