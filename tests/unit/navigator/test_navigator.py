from ledgered.devices import DeviceType, Devices
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, patch

from ragger.backend import SpeculosBackend, LedgerCommBackend
from ragger.navigator import BaseNavInsID, Navigator, NavIns, NavInsID


class TestNavigator(TestCase):

    def setUp(self):
        self.directory = TemporaryDirectory()
        self.backend = MagicMock()
        self.device = Devices.get_by_type(DeviceType.NANOS)
        self.callbacks = dict()
        self.navigator = Navigator(self.backend, self.device, self.callbacks)

    def tearDown(self):
        self.directory.cleanup()

    @property
    def pathdir(self) -> Path:
        return Path(self.directory.name)

    def test__get_snaps_dir_path(self):
        name = "some_name"
        expected = self.pathdir / "snapshots-tmp" / self.device.name / name
        result = self.navigator._get_snaps_dir_path(self.pathdir, name, False)
        self.assertEqual(result, expected)

        expected = self.pathdir / "snapshots" / self.device.name / name
        result = self.navigator._get_snaps_dir_path(self.pathdir, name, True)
        self.assertEqual(result, expected)

    def test__checks_snaps_dir_path_ok_creates_dir(self):
        name = "some_name"
        expected = self.pathdir / "snapshots" / self.device.name / name
        navigator = Navigator(self.backend, self.device, self.callbacks, golden_run=True)
        self.assertFalse(expected.exists())
        result = navigator._check_snaps_dir_path(self.pathdir, name, True)
        self.assertEqual(result, expected)
        self.assertTrue(expected.exists())

    def test__checks_snaps_dir_path_ok_dir_exists(self):
        name = "some_name"
        expected = self.pathdir / "snapshots" / self.device.name / name
        navigator = Navigator(self.backend, self.device, self.callbacks, golden_run=True)
        expected.mkdir(parents=True)
        self.assertTrue(expected.exists())
        result = navigator._check_snaps_dir_path(self.pathdir, name, True)
        self.assertEqual(result, expected)
        self.assertTrue(expected.exists())

    def test__checks_snaps_dir_path_nok_raises(self):
        name = "some_name"
        expected = self.pathdir / "snapshots" / self.device.name / name
        self.assertFalse(expected.exists())
        with self.assertRaises(ValueError):
            self.navigator._check_snaps_dir_path(self.pathdir, name, True)
        self.assertFalse(expected.exists())

    def test___init_snaps_temp_dir_ok_creates_dir(self):
        name = "some_name"
        expected = self.pathdir / "snapshots-tmp" / self.device.name / name
        self.assertFalse(expected.exists())
        result = self.navigator._init_snaps_temp_dir(self.pathdir, name)
        self.assertEqual(result, expected)
        self.assertTrue(expected.exists())

    def test___init_snaps_temp_dir_ok_unlink_files(self):
        for start_idx in [0, 1]:
            existing_files = ["00000.png", "00001.png", "00002.png"]
            name = "some_name"
            expected = self.pathdir / "snapshots-tmp" / self.device.name / name
            expected.mkdir(parents=True, exist_ok=True)
            for filename in existing_files:
                (expected / filename).touch()
                self.assertTrue((expected / filename).exists())
            if start_idx:
                result = self.navigator._init_snaps_temp_dir(self.pathdir, name, start_idx)
            else:
                result = self.navigator._init_snaps_temp_dir(self.pathdir, name)
            self.assertEqual(result, expected)
            self.assertTrue(expected.exists())
            for filename in existing_files[start_idx:]:
                self.assertFalse((expected / filename).exists())

    def test__get_snap_path(self):
        path = Path("not important")
        testset = {1: "00001", 11: "00011", 111: "00111", 1111: "01111", 11111: "11111"}
        for (index, name) in testset.items():
            name += ".png"
            self.assertEqual(self.navigator._get_snap_path(path, index), path / name)

    def test__compare_snap_with_timeout_ok(self):
        self.navigator._backend.compare_screen_with_snapshot.side_effect = [False, True]
        self.assertTrue(self.navigator._compare_snap_with_timeout("not important", 1))
        self.assertEqual(self.navigator._backend.compare_screen_with_snapshot.call_count, 2)

    def test__compare_snap_with_timeout_ok_no_timeout(self):
        self.navigator._backend.compare_screen_with_snapshot.return_value = True
        self.assertTrue(self.navigator._compare_snap_with_timeout("not important", 0))
        self.assertEqual(self.navigator._backend.compare_screen_with_snapshot.call_count, 1)

    def test__compare_snap_with_timeout_nok(self):
        self.navigator._backend.compare_screen_with_snapshot.return_value = False
        self.assertFalse(self.navigator._compare_snap_with_timeout("not important", 0))
        self.assertEqual(self.navigator._backend.compare_screen_with_snapshot.call_count, 1)

    def test_compare_snap_ok(self):
        self.navigator._backend.compare_screen_with_snapshot.return_value = True
        self.assertIsNone(self.navigator._compare_snap(self.pathdir, self.pathdir, 1))

    def test_compare_snap_nok_raises(self):
        self.navigator._backend.compare_screen_with_snapshot.return_value = False
        with self.assertRaises(AssertionError):
            self.navigator._compare_snap(self.pathdir, self.pathdir, 1)

    def test__run_instructions_nok_no_callback(self):
        instruction = NavIns(NavInsID.WAIT)
        with self.assertRaises(NotImplementedError):
            self.navigator._run_instruction(instruction)

    def test__run_instructions_NavIns(self):
        cb_wait = MagicMock()
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait}
        args, kwargs = ("some", "args"), {"1": 2}
        instruction = NavIns(NavInsID.WAIT, args, kwargs)
        self.assertIsNone(self.navigator._run_instruction(instruction))
        self.assertEqual(cb_wait.call_count, 1)
        self.assertEqual(cb_wait.call_args, (args, kwargs))

    def test__run_instructions_NavInsID(self):
        cb_wait = MagicMock()
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait}
        self.assertIsNone(self.navigator._run_instruction(NavInsID.WAIT))
        self.assertEqual(cb_wait.call_count, 1)
        self.assertEqual(cb_wait.call_args, ((), ))

    def test__run_instructions_custom_instruction(self):

        class TestInsID(BaseNavInsID):
            WAIT = 1

        cb_wait = MagicMock()
        self.navigator._callbacks = {TestInsID.WAIT: cb_wait}
        self.assertIsNone(self.navigator._run_instruction(TestInsID.WAIT))
        self.assertEqual(cb_wait.call_count, 1)
        self.assertEqual(cb_wait.call_args, ((), ))

    def test_navigate_nok_raises(self):
        with self.assertRaises(NotImplementedError):
            self.navigator.navigate([NavIns(2)])

    def test_navigate_ok(self):
        cb_wait, cb1, cb2 = MagicMock(), MagicMock(), MagicMock()
        ni1, ni2, ni3 = NavIns(1, (1, ), {'1': 1}), NavIns(2, (2, ), {'2': 2}), NavInsID.WAIT
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait, ni1.id: cb1, ni2.id: cb2}
        self.navigator.navigate([ni1, ni2, ni3])
        self.assertEqual(cb_wait.call_count, 2)
        self.assertEqual(cb_wait.call_args, ((), ))
        for cb, ni in [(cb1, ni1), (cb2, ni2)]:
            self.assertEqual(cb.call_count, 1)
            self.assertEqual(cb.call_args, (ni.args, ni.kwargs))

    def test_navigate_and_compare_ok(self):
        cb_wait, cb1, cb2 = MagicMock(), MagicMock(), MagicMock()
        ni1, ni2 = NavIns(1, (1, ), {'1': 1}), NavIns(2, (2, ), {'2': 2})
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait, ni1.id: cb1, ni2.id: cb2}
        self.navigator._backend = MagicMock(spec=SpeculosBackend)
        self.navigator._compare_snap = MagicMock()
        self.navigator.navigate_and_compare(self.pathdir,
                                            self.pathdir, [ni1, ni2],
                                            screen_change_before_first_instruction=True,
                                            screen_change_after_last_instruction=True)

        # backend wait_for_screen_change function called 3 times
        self.assertEqual(self.navigator._backend.wait_for_screen_change.call_count, 3)

        # snapshots checked, so 3 calls
        self.assertEqual(self.navigator._compare_snap.call_count, 3)

        self.assertEqual(cb_wait.call_count, 1)

        for cb, ni in [(cb1, ni1), (cb2, ni2)]:
            self.assertEqual(cb.call_count, 1)
            self.assertEqual(cb.call_args, (ni.args, ni.kwargs))

    def test_navigate_until_text_and_compare_ok_no_snapshots(self):
        self.navigator._backend = MagicMock(spec=SpeculosBackend)
        self.navigator._backend.compare_screen_with_text.side_effect = [False, False, True]
        self.navigator._run_instruction = MagicMock()
        text = "some triggering text"
        cb_wait, cb1, cb2 = MagicMock(), MagicMock(), MagicMock()
        ni1, ni2 = NavIns(1, (1, ), {'1': 1}), NavIns(2, (2, ), {'2': 2})
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait, ni1.id: cb1, ni2.id: cb2}
        self.navigator._compare_snap = MagicMock()

        self.assertIsNone(self.navigator.navigate_until_text_and_compare(ni1, [ni2], text))
        # no snapshot to check, so no call
        self.assertFalse(self.navigator._compare_snap.called)
        # backend compare function called 3 times with the text
        self.assertEqual(self.navigator._backend.compare_screen_with_text.call_count, 3)
        self.assertEqual(self.navigator._backend.compare_screen_with_text.call_args_list,
                         [((text, ), )] * 3)
        # backend compare function return 2 time False, then True
        # so 2 calls with the navigate instruction, and the final one with the validation instruction
        self.assertEqual(self.navigator._run_instruction.call_count, 5)
        self.assertEqual(self.navigator._run_instruction.call_args_list[0][0][0].id, NavInsID.WAIT)
        self.assertEqual(self.navigator._run_instruction.call_args_list[1][0][0], ni1)
        self.assertEqual(self.navigator._run_instruction.call_args_list[2][0][0], ni1)
        self.assertEqual(self.navigator._run_instruction.call_args_list[3][0][0].id, NavInsID.WAIT)
        self.assertEqual(self.navigator._run_instruction.call_args_list[4][0][0], ni2)

    def test_navigate_until_text_and_compare_ok_with_snapshots(self):
        self.navigator._backend = MagicMock(spec=SpeculosBackend)
        self.navigator._backend.compare_screen_with_text.side_effect = [False, False, True]
        self.navigator._run_instruction = MagicMock()
        text = "some triggering text"
        cb_wait, cb1, cb2 = MagicMock(), MagicMock(), MagicMock()
        ni1, ni2 = NavIns(1, (1, ), {'1': 1}), NavIns(2, (2, ), {'2': 2})
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait, ni1.id: cb1, ni2.id: cb2}
        self.navigator._compare_snap = MagicMock()

        self.assertIsNone(
            self.navigator.navigate_until_text_and_compare(ni1, [ni2], text, self.pathdir,
                                                           self.pathdir))
        # backend compare function called 3 times with the text
        self.assertEqual(self.navigator._backend.compare_screen_with_text.call_count, 3)
        self.assertEqual(self.navigator._backend.compare_screen_with_text.call_args_list,
                         [((text, ), )] * 3)
        # backend compare function return 2 time False, then True
        # so 2 calls with the navigate instruction, and the final one with the validation instruction
        self.assertEqual(self.navigator._run_instruction.call_count, 5)
        self.assertEqual(self.navigator._run_instruction.call_args_list[0][0][0].id, NavInsID.WAIT)
        self.assertEqual(self.navigator._run_instruction.call_args_list[1][0][0], ni1)
        self.assertEqual(self.navigator._run_instruction.call_args_list[2][0][0], ni1)
        self.assertEqual(self.navigator._run_instruction.call_args_list[3][0][0].id, NavInsID.WAIT)
        self.assertEqual(self.navigator._run_instruction.call_args_list[4][0][0], ni2)

    def test_navigate_until_text_and_compare_nok_timeout(self):
        self.navigator._backend = MagicMock(spec=SpeculosBackend)
        self.navigator._backend.compare_screen_with_text.return_value = False
        self.navigator.navigate = MagicMock()
        cb_wait, cb = MagicMock(), MagicMock()
        ni = NavIns(1, (1, ), {'1': 1})
        self.navigator._callbacks = {NavInsID.WAIT: cb_wait, ni.id: cb}
        self.navigator._compare_snap = MagicMock()

        with self.assertRaises(TimeoutError):
            self.navigator.navigate_until_text_and_compare(ni, [], "not important", timeout=0)

    def test_navigate_until_snap_not_speculos(self):
        self.navigator._backend = MagicMock(spec=LedgerCommBackend)
        self.assertEqual(
            0,
            self.navigator.navigate_until_snap(NavInsID.WAIT, NavInsID.WAIT, Path(), Path(), "",
                                               ""))

    def test_navigate_until_snap_ok(self):
        self.navigator._backend = MagicMock(spec=SpeculosBackend)
        self.navigator._check_snaps_dir_path = MagicMock()
        self.navigator._run_instruction = MagicMock()
        self.navigator._compare_snap_with_timeout = MagicMock()
        snapshot_comparisons = (True, True, False)
        # comparing first snapshot: True
        # then comparing snapshots until given: True (i.e first snapshot is the expected one)
        # then waiting for a screen change: False (screen changed)
        expected_idx = 0
        # as there is no snapshot between the first image and the last snapshot, the index is 0
        self.navigator._compare_snap_with_timeout.side_effect = snapshot_comparisons
        self.assertEqual(
            expected_idx,
            self.navigator.navigate_until_snap(NavInsID.WAIT, NavInsID.WAIT, Path(), Path(), "",
                                               ""))

        snapshot_comparisons = (True, False, False, True, False)
        # comparing first snapshot: True
        # then comparing snapshots until given: False, False, True (i.e first two snapshots did not match, but the third is the expected one)
        # then waiting for a screen change: False (screen changed)
        expected_idx = 2
        # as there is 2 snapshots between the first image and the last snapshot, the index is 0
        self.navigator._compare_snap_with_timeout.side_effect = snapshot_comparisons
        self.assertEqual(
            expected_idx,
            self.navigator.navigate_until_snap(NavInsID.WAIT, NavInsID.WAIT, Path(), Path(), "",
                                               ""))

    def test_navigate_until_snap_nok_timeout(self):
        self.navigator._backend = MagicMock(spec=SpeculosBackend)
        self.navigator._check_snaps_dir_path = MagicMock()
        self.navigator._run_instruction = MagicMock()
        self.navigator._compare_snap_with_timeout = MagicMock()
        self.navigator._compare_snap_with_timeout.return_value = True
        with patch("ragger.navigator.navigator.LAST_SCREEN_UPDATE_TIMEOUT", 0):
            with self.assertRaises(TimeoutError):
                self.navigator.navigate_until_snap(NavInsID.WAIT,
                                                   NavInsID.WAIT,
                                                   Path(),
                                                   Path(),
                                                   "",
                                                   "",
                                                   timeout=0)
