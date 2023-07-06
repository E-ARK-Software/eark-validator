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

from enum import Enum

from importlib_resources import files

from ip_validation import rules as SC
import tests.resources.schematron as SCHEMATRON
import tests.resources.xml as XML

PERSON_XML = 'person.xml'
PERSON_PATH = str(files(SCHEMATRON).joinpath(PERSON_XML))
NOT_FOUND_PATH = str(files(SCHEMATRON).joinpath('not-found.xml'))
EMPTY_FILE_PATH = str(files('tests.resources').joinpath('empty.file'))
METS_VALID = 'METS-valid.xml'
METS_VALID_PATH = str(files(XML).joinpath(METS_VALID))
METS_ONE_DEF = str(files(SCHEMATRON).joinpath('METS-one-default-ns.xml'))
class SchematronTest(unittest.TestCase):
    """Tests for Schematron validation rules."""
    @classmethod
    def setUpClass(cls):
        cls._person_rules = SC.SchematronRuleset(PERSON_PATH)
        cls._mets_one_def_rules = SC.SchematronRuleset(METS_ONE_DEF)

    def test_path(self):
        self.assertEqual(self._person_rules.path, PERSON_PATH)
        self.assertEqual(self._mets_one_def_rules.path, METS_ONE_DEF)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            SC.SchematronRuleset(NOT_FOUND_PATH)

    def test_dir_value_err(self):
        with self.assertRaises(ValueError):
            SC.SchematronRuleset(str(files(SCHEMATRON)))

    def test_empty_file(self):
        with self.assertRaises(ValueError):
            SC.SchematronRuleset(EMPTY_FILE_PATH)

    def test_notschematron_file(self):
        with self.assertRaises(ValueError):
            SC.SchematronRuleset(str(files(XML).joinpath(PERSON_XML)))

    def test_load_schematron(self):
        assert_count = 0
        for _ in self._person_rules.get_assertions():
            assert_count += 1
        self.assertTrue(assert_count > 0)

    def test_validate_person(self):
        self._person_rules.validate(str(files(XML).joinpath(PERSON_XML)))
        self.assertTrue(SC.TestReport.from_validation_report(self._person_rules._schematron.validation_report).is_valid)

    def test_validate_invalid_person(self):
        self._person_rules.validate(str(files(XML).joinpath('invalid-person.xml')))
        self.assertFalse(SC.TestReport.from_validation_report(self._person_rules._schematron.validation_report).is_valid)

    def test_validate_mets(self):
        self._mets_one_def_rules.validate(METS_VALID_PATH)
        self.assertTrue(SC.TestReport.from_validation_report(self._mets_one_def_rules._schematron.validation_report).is_valid)

    def test_validate_mets_no_root(self):
        self._mets_one_def_rules.validate(str(files(XML).joinpath('METS-no-root.xml')))
        self.assertFalse(SC.TestReport.from_validation_report(self._mets_one_def_rules._schematron.validation_report).is_valid)

    def test_validate_mets_no_objid(self):
        self._mets_one_def_rules.validate(str(files(XML).joinpath('METS-no-objid.xml')))
        self.assertFalse(SC.TestReport.from_validation_report(self._mets_one_def_rules._schematron.validation_report).is_valid)
