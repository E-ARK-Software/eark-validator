#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# E-ARK Validation
# Copyright (C) 2019
# All rights reserved.
#
# Licensed to the E-ARK project under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The E-ARK project licenses
# this file to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

from enum import Enum
from pathlib import Path
import os
import unittest

from eark_validator.infopacks.manifest import Checksummer
from eark_validator.infopacks.package_handler import PackageError, PackageHandler

from eark_validator.model import StructureStatus, StructResults

MIN_TAR_SHA1 = '47CA3A9D7F5F23BF35B852A99785878C5E543076'

class TestStatus(Enum):
    __test__ = False
    Illegal = 5

class StatusValuesTest(unittest.TestCase):
    """Tests for package and manifest status values."""
    def test_lgl_pckg_status(self):
        for status in list(StructureStatus):
            results = StructResults(status=status, messages=[])
            self.assertEqual(results.status, status)

    def test_illgl_pckg_status(self):
        self.assertRaises(ValueError, StructResults, status=TestStatus.Illegal)

class PackageHandlerTest(unittest.TestCase):
    dir_path = Path(os.path.join(os.path.dirname(__file__), 'resources'))
    empty_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'empty.file'))
    not_exists_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'not_there.zip'))
    min_tar_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                                'minimal_IP_with_schemas.tar'))
    min_zip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                                'minimal_IP_with_schemas.zip'))
    min_targz_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                                  'minimal_IP_with_schemas.tar.gz'))
    multi_dir_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'bad',
                                  'multi_dir.zip'))
    single_file_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'bad',
                                  'single_file.zip'))

    def test_sha1(self):
        sha1 = Checksummer.from_file(self.empty_path, 'SHA-1').value
        self.assertEqual(sha1, 'DA39A3EE5E6B4B0D3255BFEF95601890AFD80709')
        sha1 = Checksummer.from_file(self.min_tar_path, 'SHA-1').value
        self.assertEqual(sha1, MIN_TAR_SHA1)

    def test_is_archive(self):
        self.assertTrue(PackageHandler.is_archive(self.min_tar_path))
        self.assertTrue(PackageHandler.is_archive(self.min_zip_path))
        self.assertTrue(PackageHandler.is_archive(self.min_targz_path))
        self.assertFalse(PackageHandler.is_archive(self.empty_path))

    def test_unpack_illgl_archive(self):
        handler = PackageHandler()
        self.assertRaises(ValueError, handler.unpack_package, self.empty_path)

    def test_multi_dir(self):
        handler = PackageHandler()
        self.assertRaises(PackageError, handler.unpack_package, self.multi_dir_path)

    def test_single_file(self):
        handler = PackageHandler()
        self.assertRaises(PackageError, handler.unpack_package, self.single_file_path)

    def test_prepare_not_exists(self):
        handler = PackageHandler()
        self.assertRaises(ValueError, handler.prepare_package, self.not_exists_path)

    def test_unpack_archives(self):
        handler = PackageHandler()
        dest = Path(handler.unpack_package(self.min_tar_path))
        self.assertEqual(os.path.basename(dest.parent), MIN_TAR_SHA1)
        dest = Path(handler.unpack_package(self.min_zip_path))
        self.assertEqual(os.path.basename(dest.parent), '54BBE654FE332B51569BAF21338BC811CAD2AF66')
        dest = Path(handler.unpack_package(self.min_targz_path))
        self.assertEqual(os.path.basename(dest.parent), 'DB2703FF464E613E9D1DC5C495E23A2E2D49B89D')

    def test_is_dir_archive(self):
        self.assertFalse(PackageHandler.is_archive(self.dir_path))

if __name__ == '__main__':
    unittest.main()
