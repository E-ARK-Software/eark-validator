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

import unittest

from importlib_resources import files

import tests.resources.xml as XML
import tests.resources.ips.unpacked as UNPACKED

from eark_validator.infopacks.information_package import PackageDetails
from eark_validator.xml.schema import LOCAL_SCHEMA, get_local_schema

METS_XML = 'METS.xml'

class PackageDetailsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mets_file = str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031').joinpath(METS_XML))

    def test_not_exists(self):
        with self.assertRaises(FileNotFoundError):
            PackageDetails.from_mets_file('not-exists.xml')

    def test_isdir(self):
        with self.assertRaises(ValueError):
            PackageDetails.from_mets_file(str(files(XML)))

    """Tests for Schematron validation rules."""
    def test_objid(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.objid, '733dc055-34be-4260-85c7-5549a7083031')

    def test_label(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.label, '')

    def  test_type(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.type, 'Other')

    def test_othertype(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.othertype, 'type')

    def test_contentinformationtype(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.contentinformationtype, 'MIXED')

    def test_profile(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.profile, 'NOT_DEFINED')

    def test_oaispackagetype(self):
        parser = PackageDetails.from_mets_file(self._mets_file)
        self.assertEqual(parser.oaispackagetype, 'AIP')

class SchemaTest(unittest.TestCase):
    def test_schema(self):
        for namespace in LOCAL_SCHEMA:
            schema = get_local_schema(namespace)
            self.assertIsNotNone(schema)

if __name__ == '__main__':
    unittest.main()
