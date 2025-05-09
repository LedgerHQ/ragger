from unittest import TestCase
from unittest.mock import MagicMock
from ledgered.devices import Devices, DeviceType

from ragger.firmware.touch import FullScreen
from ragger.firmware.touch.positions import POSITIONS


class TestFullScreen(TestCase):

    def setUp(self):
        self.backend = MagicMock()
        self.device = Devices.get_by_type(DeviceType.STAX)
        self.screen = FullScreen(self.backend, self.device)

    def test_non_variable_layouts(self):
        # all of this layouts only have a 'tap' method with no argument,
        # which translate to a backend.touch_finger on a fixed position
        layout_positions = [
            (self.screen.right_header, POSITIONS["RightHeader"][self.device.type]),
            (self.screen.exit_header, POSITIONS["RightHeader"][self.device.type]),
            (self.screen.info_header, POSITIONS["RightHeader"][self.device.type]),
            (self.screen.left_header, POSITIONS["LeftHeader"][self.device.type]),
            (self.screen.navigation_header, POSITIONS["LeftHeader"][self.device.type]),
            (self.screen.tappable_center, POSITIONS["TappableCenter"][self.device.type]),
            (self.screen.centered_footer, POSITIONS["CenteredFooter"][self.device.type]),
            (self.screen.cancel_footer, POSITIONS["CancelFooter"][self.device.type]),
            (self.screen.exit_footer, POSITIONS["CancelFooter"][self.device.type]),
            (self.screen.info_footer, POSITIONS["CancelFooter"][self.device.type]),
            (self.screen.settings_footer, POSITIONS["CancelFooter"][self.device.type]),
        ]
        call_number = 0
        self.assertEqual(self.backend.finger_touch.call_count, call_number)
        for (layout, position) in layout_positions:
            # each of this
            layout.tap()
            call_number += 1
            self.assertEqual(self.backend.finger_touch.call_count, call_number)
            self.assertEqual(self.backend.finger_touch.call_args, ((*position, ), ))

    def test_choosing_layouts(self):
        layout_index_positions = [
            (self.screen.choice_list, 1, POSITIONS["ChoiceList"][self.device.type]),
            (self.screen.suggestions, 2, POSITIONS["Suggestions"][self.device.type]),
        ]
        call_number = 0
        self.assertEqual(self.backend.finger_touch.call_count, call_number)
        for (layout, index, position) in layout_index_positions:
            # each of this
            layout.choose(index)
            call_number += 1
            self.assertEqual(self.backend.finger_touch.call_count, call_number)
            self.assertEqual(self.backend.finger_touch.call_args, ((*position[index], ), ))

    def test_keyboards_common_functions(self):
        layouts_word_positions = [
            (self.screen.letter_only_keyboard, "basicword",
             POSITIONS["LetterOnlyKeyboard"][self.device.type]),
            (self.screen.full_keyboard_letters, "still basic",
             POSITIONS["FullKeyboardLetters"][self.device.type]),
            (self.screen.full_keyboard_special_characters_1, "12)&@'.",
             POSITIONS["FullKeyboardSpecialCharacters1"][self.device.type]),
            (self.screen.full_keyboard_special_characters_2, "[$?~+*|",
             POSITIONS["FullKeyboardSpecialCharacters2"][self.device.type]),
        ]
        self.assertEqual(self.backend.finger_touch.call_count, 0)
        for (layout, word, positions) in layouts_word_positions:

            layout.write(word)
            argument_list = [((*positions[letter], ), ) for letter in word]
            call_number = len(word)
            self.assertEqual(self.backend.finger_touch.call_count, call_number)
            self.assertEqual(self.backend.finger_touch.call_args_list, argument_list)

            layout.back()
            self.assertEqual(self.backend.finger_touch.call_count, call_number + 1)
            self.assertEqual(self.backend.finger_touch.call_args, ((*positions["back"], ), ))

            self.backend.finger_touch.reset_mock()

    def test_keyboards_change_layout(self):
        layouts_positions = [
            (self.screen.full_keyboard_letters, POSITIONS["FullKeyboardLetters"][self.device.type]),
            (self.screen.full_keyboard_special_characters_1,
             POSITIONS["FullKeyboardSpecialCharacters1"][self.device.type]),
            (self.screen.full_keyboard_special_characters_2,
             POSITIONS["FullKeyboardSpecialCharacters2"][self.device.type]),
        ]
        call_number = 0
        self.assertEqual(self.backend.finger_touch.call_count, call_number)
        for layout, positions in layouts_positions:
            layout.change_layout()
            call_number += 1
            self.assertEqual(self.backend.finger_touch.call_count, call_number)
            self.assertEqual(self.backend.finger_touch.call_args,
                             ((*positions["change_layout"], ), ))

    def test_keyboards_change_case(self):
        self.assertEqual(self.backend.finger_touch.call_count, 0)
        self.screen.full_keyboard_letters.change_case()
        self.assertEqual(self.backend.finger_touch.call_count, 1)
        self.assertEqual(self.backend.finger_touch.call_args,
                         ((*POSITIONS["FullKeyboardLetters"][self.device.type]["change_case"], ), ))

    def test_keyboards_change_special_characters(self):
        layouts_positions = [
            (self.screen.full_keyboard_special_characters_1,
             POSITIONS["FullKeyboardSpecialCharacters2"][self.device.type]),
            (self.screen.full_keyboard_special_characters_2,
             POSITIONS["FullKeyboardSpecialCharacters2"][self.device.type]),
        ]
        call_number = 0
        self.assertEqual(self.backend.finger_touch.call_count, call_number)
        for layout, positions in layouts_positions:
            layout.more_specials()
            call_number += 1
            self.assertEqual(self.backend.finger_touch.call_count, call_number)
            self.assertEqual(self.backend.finger_touch.call_args,
                             ((*positions["more_specials"], ), ))
