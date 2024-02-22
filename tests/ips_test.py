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

import os
from pathlib import Path
import unittest

from importlib_resources import files
from eark_validator.model.package_details import InformationPackage

import tests.resources.xml as XML
import tests.resources.ips.unpacked as UNPACKED

from eark_validator.infopacks.information_package import InformationPackages
from eark_validator.ipxml.schema import LOCAL_SCHEMA, get_local_schema

METS_XML = 'METS.xml'

class PackageDetailsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mets_file = Path(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031').joinpath(METS_XML))

    def test_not_exists(self):
        with self.assertRaises(FileNotFoundError):
            InformationPackages.details_from_mets_file(Path('not-exists.xml'))

    def test_isdir(self):
        with self.assertRaises(ValueError):
            InformationPackages.details_from_mets_file(Path(files(XML)))

    def test_bad_xml(self):
        with self.assertRaises(ValueError):
            InformationPackages.details_from_mets_file(Path(files(XML).joinpath('METS-no-hdr.xml')))

    def test_label(self):
        package_details = InformationPackages.details_from_mets_file(self._mets_file)
        self.assertEqual(package_details.label, '')

    def test_othertype(self):
        package_details = InformationPackages.details_from_mets_file(self._mets_file)
        self.assertEqual(package_details.othertype, 'type')

    def test_contentinformationtype(self):
        package_details = InformationPackages.details_from_mets_file(self._mets_file)
        self.assertEqual(package_details.contentinformationtype, 'MIXED')

    def test_oaispackagetype(self):
        package_details = InformationPackages.details_from_mets_file(self._mets_file)
        self.assertEqual(package_details.oaispackagetype, 'AIP')

class InformationPackageTest(unittest.TestCase):
    def test_from_path_not_exists(self):
        with self.assertRaises(FileNotFoundError):
            InformationPackages.from_path(Path('not-exists'))

    def test_from_path_not_archive(self):
        with self.assertRaises(ValueError):
            InformationPackages.from_path(Path(os.path.join(os.path.dirname(__file__), 'resources', 'empty.file')))

    def test_from_path_dir_no_mets(self):
        with self.assertRaises(ValueError):
            InformationPackages.from_path(Path(files(UNPACKED)))

    def test_from_path_dir(self):
        ip: InformationPackage = InformationPackages.from_path(Path(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')))
        self.assertEqual(ip.name, '733dc055-34be-4260-85c7-5549a7083031')

class SchemaTest(unittest.TestCase):
    def test_schema(self):
        for namespace in LOCAL_SCHEMA:
            schema = get_local_schema(namespace)
            self.assertIsNotNone(schema)

if __name__ == '__main__':
    unittest.main()
