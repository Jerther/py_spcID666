import glob
import os
import shutil

from base_test import BaseTest

import spcid666


class TestSpcID666Write(BaseTest):
    def tearDown(self):
        for f in glob.glob("res/*_tmp"):
            os.remove(f)

    def test_write_base(self):
        self.maxDiff = None
        tmp_file = self._get_spc_copy('res/test_sounds_empty_tags.spc')
        tag = spcid666.parse(tmp_file)
        tag.base.fadeout_length = 10,
        tag.base.title = 'Les Miserables',
        tag.base.artist = 'Victor Hugo',
        tag.base.comments = 'Really long',
        tag.base.game = 'Bookz',
        tag.base.length_before_fadeout = 11,
        tag.base.emulator.code = 1,
        tag.base.date = '2018-12-08',
        tag.base.dumper = 'Jerther',
        tag.base.muted_channels = 1
        spcid666.save(tag, tmp_file)

        expected_base = {
            'fadeout_length': 10,
            'title': u'Les Miserables',
            'artist': u'Victor Hugo',
            'comments': u'Really long',
            'is_binary': False,
            'game': u'Bookz',
            'length_before_fadeout': 11,
            'emulator': 'ZSNES',
            'date': u'2018-12-08',
            'dumper': u'Jerther',
            'muted_channels': 1
        }
        actual_tag = spcid666.parse(tmp_file)
        self.assertIsNone(actual_tag.extended)
        self._assert_base_tag_equal(expected_base, actual_tag.base)

    def _get_spc_copy(self, file_name):
        dst = '%s_tmp' % file_name
        shutil.copyfile(file_name, dst)
        return dst

    def test_write_extended_overwrite(self):
        pass

    def test_write_extended_create(self):
        pass
