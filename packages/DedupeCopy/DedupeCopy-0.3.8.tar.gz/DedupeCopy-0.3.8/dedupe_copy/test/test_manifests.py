"""Tests around loading and saving manifests"""


import os
import unittest

import utils

from dedupe_copy import dedupe_copy
from dedupe_copy.disk_cache_dict import DefaultCacheDict


class TestManifests(unittest.TestCase):

    """Test load/save of manifests individually and in a group. These are
    happy path tests.
    """

    def setUp(self):
        """Create temporary directory and test data"""
        self.temp_dir = utils.make_temp_dir('manifests')
        self.temp_dict = os.path.join(self.temp_dir, 'tempdict.dict')
        self.scratch_dict = os.path.join(self.temp_dir, 'scratch.dict')
        self.manifest_path = os.path.join(self.temp_dir, 'manifest.dict')
        self.read_path = '{0}.read'.format(self.manifest_path)
        self.manifest = dedupe_copy.Manifest(None,
                                             save_path=None,
                                             temp_directory=self.temp_dir)

    def tearDown(self):
        """Remove temporary directory and all test files"""
        del self.manifest
        utils.remove_dir(self.temp_dir)

    def setup_manifest(self):
        md5data, sources = utils.gen_fake_manifest()
        md5data = _dcd_from_manifest(md5data, self.temp_dict)
        sources = _dcd_from_manifest(sources, self.scratch_dict)
        self.manifest.md5_data = md5data
        self.manifest.read_sources = sources
        return md5data, sources

    def check_manifest(self, manifest, md5_data, sources):
        print manifest.md5_data.items()
        print manifest.read_sources.items()
        print md5_data.items()
        print sources.items()
        self.assertEqual(sorted(sources.keys()),
                         sorted(manifest.read_sources.keys()),
                         'sources does not agree with manifest sources')
        self.assertEqual(sorted(md5_data.keys()),
                         sorted(manifest.md5_data.keys()),
                         'data keys does not agree')
        for key, values in md5_data.iteritems():
            for index, meta_data in enumerate(values):
                self.assertEqual(meta_data, manifest.md5_data[key][index],
                                 'Meta data mismatch for key {}'.format(key))
        del md5_data
        del sources

    def test_save(self):
        """Create a manifest, save it and directly get a DCD to test"""
        md5data, sources = self.setup_manifest()
        self.manifest.save(path=self.manifest_path)
        dcd_check = DefaultCacheDict(list, db_file=self.manifest_path)
        sources_check = DefaultCacheDict(list, db_file=self.read_path)
        self.check_manifest(self.manifest, md5data, sources)
        self.check_manifest(self.manifest, dcd_check, sources_check)
        del md5data
        del sources

    def test_manifest_conversion(self):
        """Manifest path translation"""
        md5data, sources = self.setup_manifest()
        self.manifest.save(path=self.manifest_path)
        self.manifest.convert_manifest_paths('/a/b', '/fred',
                                             temp_directory=self.temp_dir)
        for path in self.manifest.read_sources.keys():
            self.assertTrue((not path.startswith('/a/b')) and
                            (path.startswith('/c/b') or path.startswith('/fred')))
        for metadata in self.manifest.md5_data.values():
            for items in metadata:
                path = items[0]
                self.assertTrue((not path.startswith('/a/b')) and
                                (path.startswith('/c/b') or path.startswith('/fred')))
        del md5data
        del sources

    def test_load_single(self):
        """Load a previously saved manifest"""
        md5data, sources = utils.gen_fake_manifest()
        md5data = _dcd_from_manifest(md5data, self.temp_dict)
        sources = _dcd_from_manifest(
            sources, '{0}.read'.format(self.temp_dict))
        md5data.save()
        sources.save()
        manifest = dedupe_copy.Manifest(self.temp_dict,
                                        temp_directory=self.temp_dir)
        self.check_manifest(manifest, md5data, sources)
        del md5data
        del sources

    def test_load_list(self):
        """Loading a list of manifests"""
        master_md5 = {}
        master_sources = {}
        paths = []
        for i in range(5):
            md5data, sources = utils.gen_fake_manifest()
            path = '{0}{1}'.format(self.temp_dict, i)
            paths.append(path)
            md5data = _dcd_from_manifest(md5data, path)
            sources = _dcd_from_manifest(sources, '{0}.read'.format(path))
            md5data.save()
            sources.save()
            master_md5.update(md5data)
            master_sources.update(sources)
        combined = dedupe_copy.Manifest(paths, temp_directory=self.temp_dir)
        self.check_manifest(combined, master_md5, master_sources)
        del md5data
        del sources


def _dcd_from_manifest(data, path):
    dcd = DefaultCacheDict(list, db_file=path)
    dcd.update(data)
    return dcd
