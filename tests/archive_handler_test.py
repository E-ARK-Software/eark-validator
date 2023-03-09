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
import os
import unittest

from ip_validation.infopacks import structure as STRUCT
from ip_validation.infopacks.manifest import Checksum

MIN_TAR_SHA1 = '47ca3a9d7f5f23bf35b852a99785878c5e543076'

class TestStatus(Enum):
    __test__ = False
    Illegal = 5

class StatusValuesTest(unittest.TestCase):
    """Tests for package and manifest status values."""
    def test_lgl_pckg_status(self):
        for status in list(STRUCT.StructureStatus):
            details = STRUCT.StructureReport(status=status)
            self.assertTrue(details.status == status)

    def test_illgl_pckg_status(self):
        self.assertRaises(ValueError, STRUCT.StructureReport, status=TestStatus.Illegal)

class ArchiveHandlerTest(unittest.TestCase):
    empty_path = os.path.join(os.path.dirname(__file__), 'resources', 'empty.file')
    min_tar_path = os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                                'minimal_IP_with_schemas.tar')
    min_zip_path = os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                                'minimal_IP_with_schemas.zip')
    min_targz_path = os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                                  'minimal_IP_with_schemas.tar.gz')

    def test_sha1(self):
        sha1 = Checksum.from_file(self.empty_path, 'SHA1').value
        self.assertTrue(sha1 == 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
        sha1 = Checksum.from_file(self.min_tar_path, 'SHA1').value
        self.assertTrue(sha1 == MIN_TAR_SHA1)

    def test_is_archive(self):
        self.assertTrue(STRUCT.ArchivePackageHandler.is_archive(self.min_tar_path))
        self.assertTrue(STRUCT.ArchivePackageHandler.is_archive(self.min_zip_path))
        self.assertTrue(STRUCT.ArchivePackageHandler.is_archive(self.min_targz_path))
        self.assertFalse(STRUCT.ArchivePackageHandler.is_archive(self.empty_path))

    def test_unpack_illgl_archive(self):
        handler = STRUCT.ArchivePackageHandler()
        self.assertRaises(STRUCT.PackageStructError, handler.unpack_package, self.empty_path)

    def test_unpack_archives(self):
        handler = STRUCT.ArchivePackageHandler()
        dest = handler.unpack_package(self.min_tar_path)
        self.assertTrue(os.path.basename(dest) == MIN_TAR_SHA1)
        dest = handler.unpack_package(self.min_zip_path)
        self.assertTrue(os.path.basename(dest) == '54bbe654fe332b51569baf21338bc811cad2af66')
        dest = handler.unpack_package(self.min_targz_path)
        self.assertTrue(os.path.basename(dest) == 'db2703ff464e613e9d1dc5c495e23a2e2d49b89d')

if __name__ == '__main__':
    unittest.main()
