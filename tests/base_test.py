import unittest


class BaseTest(unittest.TestCase):
    def _assert_base_tag_equal(self, expected, actual):
        actual_vals = {
            'fadeout_length': actual.fadeout_length,
            'title': actual.title,
            'artist': actual.artist,
            'comments': actual.comments,
            'is_binary': actual.is_binary,
            'game': actual.game,
            'length_before_fadeout': actual.length_before_fadeout,
            'emulator': actual.emulator.name,
            'date': actual.date,
            'dumper': actual.dumper,
            'muted_channels': actual.muted_channels
        }
        self.assertDictEqual(expected, actual_vals)

    def _assert_extended_tag_equal(self, expected, actual):
        actual_vals = {
            'publisher': actual.publisher,
            'loop_length': actual.loop_length,
            'copyright': actual.copyright,
            'artist': actual.artist,
            'track': actual.track,
            'title': actual.title,
            'official_title': actual.official_title,
            'comments': actual.comments,
            'nb_loops': actual.nb_loops,
            'intro_length': actual.intro_length,
            'game': actual.game,
            'disc': actual.disc,
            'end_length': actual.end_length,
            'emulator': actual.emulator,
            'unknown_items': actual.unknown_items,
            'date': actual.date,
            'mixing_level': actual.mixing_level,
            'fade_length': actual.fade_length,
            'dumper': actual.dumper,
            'muted_channels': actual.muted_channels
        }
        self.assertDictEqual(expected, actual_vals)