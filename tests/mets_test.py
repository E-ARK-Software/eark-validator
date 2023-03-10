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

from ip_validation.mets import MetsValidator
from ip_validation.xml.schema import LOCAL_SCHEMA, get_local_schema

METS_XML = 'METS.xml'
class MetsValidatorTest(unittest.TestCase):
    """Tests for Schematron validation rules."""
    def test_mets_root(self):
        validator = MetsValidator(str(files(XML)))
        self.assertEqual(str(files(XML)), validator.root)

    def test_valid_mets(self):
        validator = MetsValidator(str(files(XML)))
        is_valid = validator.validate_mets('METS-valid.xml')
        self.assertTrue(is_valid)
        self.assertTrue(len(validator.validation_errors) == 0)

    def test_invalid_mets(self):
        validator = MetsValidator(str(files(XML)))
        is_valid = validator.validate_mets('METS-no-root.xml')
        self.assertFalse(is_valid)
        self.assertTrue(len(validator.validation_errors) > 0)

    def test_mets_no_structmap(self):
        validator = MetsValidator(str(files(XML)))
        is_valid = validator.validate_mets('METS-no-structmap.xml')
        self.assertFalse(is_valid)
        self.assertTrue(len(validator.validation_errors) > 0)

    def test_multi_mets(self):
        validator = MetsValidator(str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')))
        is_valid = validator.validate_mets(METS_XML)
        self.assertTrue(is_valid)
        self.assertTrue(len(validator.validation_errors) == 0)
        self.assertTrue(len(validator.representations) == 1)
        self.assertTrue(len(validator.file_references) > 0)
        self.assertTrue(len(validator.representation_mets) > 0)
        self.assertEqual(validator.get_mets_path('rep1'), 'representations/rep1/METS.xml')
        is_complete, issues = validator.get_manifest().check_integrity()
        self.assertTrue(is_complete)
        self.assertTrue(len(issues) == 0)

    def test_bad_manifest(self):
        validator = MetsValidator(str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031-bad')))
        is_valid = validator.validate_mets(METS_XML)
        self.assertTrue(is_valid)
        self.assertTrue(len(validator.validation_errors) == 0)
        self.assertTrue(len(validator.representations) == 1)
        self.assertTrue(len(validator.file_references) > 0)
        is_complete, issues = validator.get_manifest().check_integrity()
        self.assertFalse(is_complete)
        self.assertEqual(len(issues), 24)

class SchemaTest(unittest.TestCase):
    def test_schema(self):
        for namespace in LOCAL_SCHEMA:
            schema = get_local_schema(namespace)
            self.assertIsNotNone(schema)

if __name__ == '__main__':
    unittest.main()
