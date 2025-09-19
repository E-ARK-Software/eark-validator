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

from pathlib import Path
from importlib_resources import files
from eark_validator.infopacks.manifest import Manifests

import tests.resources.xml as XML
import tests.resources.ips.unpacked as UNPACKED

from eark_validator.mets import MetsValidator
from eark_validator.ipxml.schema import LOCAL_SCHEMA, get_local_schema

METS_XML = 'METS.xml'
class MetsValidatorTest(unittest.TestCase):
    """Tests for Schematron validation rules."""
    def test_mets_path(self):
        mets_path: Path = Path(files(XML)).joinpath('METS-valid.xml')
        validator = MetsValidator(mets_path)
        self.assertEqual(mets_path, validator._mets_path)

    def test_valid_mets(self):
        mets_path: Path = Path(files(XML)).joinpath('METS-valid.xml')
        validator = MetsValidator(mets_path)
        is_valid = validator.validate_against_schema()
        self.assertTrue(is_valid)
        self.assertEqual(len(validator.validation_errors), 0)

    def test_invalid_mets(self):
        mets_path: Path = Path(files(XML)).joinpath('METS-no-root.xml')
        validator = MetsValidator(mets_path)
        is_valid = validator.validate_against_schema()
        self.assertFalse(is_valid)
        self.assertGreater(len(validator.validation_errors), 0)

    def test_mets_no_structmap(self):
        mets_path: Path = Path(files(XML)).joinpath('METS-no-structmap.xml')
        validator = MetsValidator(mets_path)
        is_valid = validator.validate_against_schema()
        self.assertFalse(is_valid)
        self.assertGreater(len(validator.validation_errors), 0)

    def test_multi_mets(self):
        mets_path: Path = Path(files(UNPACKED)).joinpath('733dc055-34be-4260-85c7-5549a7083031').joinpath(METS_XML)
        validator = MetsValidator(mets_path)
        is_valid = validator.validate_against_schema()
        self.assertTrue(is_valid)
        self.assertEqual(len(validator.validation_errors), 0)

    def test_bad_manifest(self):
        mets_path: Path = Path(files(UNPACKED)).joinpath('733dc055-34be-4260-85c7-5549a7083031').joinpath(METS_XML)
        validator = MetsValidator(mets_path)
        is_valid = validator.validate_against_schema()
        self.assertTrue(is_valid)
        self.assertEqual(len(validator.validation_errors), 0)

class SchemaTest(unittest.TestCase):
    def test_schema(self):
        for namespace in LOCAL_SCHEMA:
            schema = get_local_schema(namespace)
            self.assertIsNotNone(schema)

if __name__ == '__main__':
    unittest.main()
