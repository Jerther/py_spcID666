import spcid666

from base_test import BaseTest


class TestSpcID666Read(BaseTest):
    def test_read_extended_tag_1(self):
        tag = spcid666.parse('res/test_808_extended_tag_1.spc')
        self.assertEqual(84, tag.extended.get_total_size())
        expected_base = {
            'fadeout_length': 9000,
            'title': u'',
            'artist': u'',
            'comments': u'',
            'is_binary': False,
            'game': u'',
            'length_before_fadeout': 828,
            'emulator': 'unknown',
            'date': u'',
            'dumper': u'',
            'muted_channels': 0
        }
        expected_ex = {
            'publisher': u'Panus',
            'loop_length': 5340800,
            'copyright': 2018,
            'artist': None,
            'track': (2, None),
            'title': None,
            'official_title': u'Ramoutz',
            'comments': None,
            'nb_loops': None,
            'intro_length': 789760,
            'game': None,
            'disc': 1,
            'end_length': 46920960,
            'emulator': None,
            'unknown_items': [],
            'date': None,
            'mixing_level': bytearray(b'\x00\x00\x01\x00'),
            'fade_length': 576000,
            'dumper': None,
            'muted_channels': 8
        }

        self._assert_base_tag_equal(expected_base, tag.base)
        self._assert_extended_tag_equal(expected_ex, tag.extended)



    def test_read_extended_tag_2(self):
        tag = spcid666.parse('res/test_808_extended_tag_2.spc')
        self.assertEqual(228, tag.extended.get_total_size())
        expected_base = {
            'fadeout_length': 9000,
            'title': u'',
            'artist': u'',
            'comments': u'',
            'is_binary': False,
            'game': u'',
            'length_before_fadeout': 828,
            'emulator': 'unknown',
            'date': u'',
            'dumper': u'',
            'muted_channels': 0
        }
        expected_ex = {
            'publisher': u"Oh look look look! It's Mama Giabb! She's flying for us! You can see her through the windows, right next to her SMOCin' son!",
            'loop_length': 5340800,
            'copyright': 2018,
            'artist': None,
            'track': (2, None),
            'title': None,
            'official_title': u'Ramoutz Panus is in the HOUSE, baby!\x11\x00\x01',
            'comments': None,
            'nb_loops': None,
            'intro_length': 789760,
            'game': None,
            'disc': None,
            'end_length': 46920960,
            'emulator': None,
            'unknown_items': [],
            'date': None,
            'mixing_level': bytearray(b'\x00\x00\x01\x00'),
            'fade_length': 576000,
            'dumper': None,
            'muted_channels': None
        }

        self._assert_base_tag_equal(expected_base, tag.base)
        self._assert_extended_tag_equal(expected_ex, tag.extended)

    def test_read_empty_tags(self):
        tag = spcid666.parse('res/test_sounds_empty_tags.spc')
        self.assertIsNone(tag.extended)
        expected_base = {
            'fadeout_length': 0,
            'title': u'',
            'artist': u'',
            'comments': u'',
            'is_binary': False,
            'game': u'',
            'length_before_fadeout': 0,
            'emulator': 'unknown',
            'date': u'',
            'dumper': u'',
            'muted_channels': 0
        }
        self._assert_base_tag_equal(expected_base, tag.base)

    def test_read_base_tag(self):
        tag = spcid666.parse('res/test_usability_base_tag.spc')
        self.assertIsNone(tag.extended)
        expected_base = {
            'fadeout_length': 5670,
            'title': u'Usability test',
            'artist': u'Shiru',
            'comments': u'This is a great comment!',
            'is_binary': False,
            'game': u'snesgss',
            'length_before_fadeout': 83,
            'emulator': 'unknown',
            'date': u'',
            'dumper': u'juef',
            'muted_channels': 0
        }
        self._assert_base_tag_equal(expected_base, tag.base)

    def test_read_base_tag_binary(self):
        tag = spcid666.parse('res/test_usability_base_tag.spc')
        self.assertIsNone(tag.extended)
        expected_base = {
            'fadeout_length': 5670,
            'title': u'Usability test',
            'artist': u'Shiru',
            'comments': u'This is a great comment!',
            'is_binary': False,
            'game': u'snesgss',
            'length_before_fadeout': 83,
            'emulator': 'unknown',
            'date': u'',
            'dumper': u'juef',
            'muted_channels': 0
        }
        self._assert_base_tag_equal(expected_base, tag.base)
