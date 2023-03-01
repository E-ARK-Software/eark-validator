#!/usr/bin/env python
# coding=UTF-8
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

from ip_validation.infopacks import rules as SC

import tests.resources.schematron as SCHEMATRON
import tests.resources.xml as XML

PERSON_PATH = str(files(SCHEMATRON).joinpath('person.xml'))
METS_VALID = 'METS-valid.xml'
METS_VALID_PATH = str(files(XML).joinpath(METS_VALID))
METS_ONE_DEF = str(files(SCHEMATRON).joinpath('METS-one-default-ns.xml'))
class ValidationRulesTest(unittest.TestCase):
    """Tests for Schematron validation rules."""
    def test_load_schematron(self):
        rules = SC.ValidationRules('test', PERSON_PATH)
        assert_count = 0
        for _ in rules.get_assertions():
            assert_count += 1
        self.assertTrue(assert_count > 0)

    def test_validate_person(self):
        rules = SC.ValidationRules('test', PERSON_PATH)
        rules.validate(str(files(XML).joinpath('person.xml')))
        self.assertTrue(rules.get_report().is_valid)

    def test_validate_invalid_person(self):
        rules = SC.ValidationRules('test', PERSON_PATH)
        rules.validate(str(files(XML).joinpath('invalid-person.xml')))
        self.assertFalse(rules.get_report().is_valid)

    def test_validate_mets(self):
        rules = SC.ValidationRules('test',
                                   METS_ONE_DEF)
        rules.validate(METS_VALID_PATH)
        self.assertTrue(rules.get_report().is_valid)

    def test_validate_mets_no_root(self):
        rules = SC.ValidationRules('test',
                                   METS_ONE_DEF)
        rules.validate(str(files(XML).joinpath('METS-no-root.xml')))
        self.assertFalse(rules.get_report().is_valid)

    def test_validate_mets_no_objid(self):
        rules = SC.ValidationRules('test',
                                   METS_ONE_DEF)
        rules.validate(str(files(XML).joinpath('METS-no-objid.xml')))
        self.assertFalse(rules.get_report().is_valid)

    def test_mets_root(self):
        result, failures, _ = _test_validation('root', METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(result)

    def test_mets_root_no_objid(self):
        result, failures, _ = _test_validation('root', 'METS-no-objid.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_no_type(self):
        result, failures, _ = _test_validation('root', 'METS-no-type.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_other_type(self):
        result, failures, _ = _test_validation('root', 'METS-other-type.xml')
        self.assertTrue(failures == 0)
        self.assertTrue(result)

    def test_mets_root_no_profile(self):
        result, failures, _ = _test_validation('root', 'METS-no-profile.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_no_hdr(self):
        result, failures, _ = _test_validation('root', 'METS-no-hdr.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_hdr_valid(self):
        result, failures, _ = _test_validation('hdr', METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(result)

    def test_mets_hdr_no_createdate(self):
        result, failures, _ = _test_validation('hdr', 'METS-no-createdate.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_hdr_no_type(self):
        result, failures, _ = _test_validation('hdr', 'METS-hdr-no-type.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_hdr_no_version(self):
        result, failures, _ = _test_validation('hdr', 'METS-hdr-no-version.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_dmd(self):
        result, _, warnings = _full_validation('root', METS_VALID)
        found_csip17 = False
        for warning in warnings:
            if warning.rule_id == 'CSIP17':
                found_csip17 = True
        self.assertTrue(found_csip17)
        self.assertTrue(result)

    def test_mets_dmd(self):
        result, failures, warnings = _test_validation('dmd', METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 0)
        self.assertTrue(result)

    def test_mets_amd(self):
        result, failures, warnings = _test_validation('amd', METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 0)
        self.assertTrue(result)

    def test_mets_file(self):
        result, failures, warnings = _test_validation('file', METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 0)
        self.assertTrue(result)

    def test_mets_structmap(self):
        result, failures, warnings = _test_validation('structmap', METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 1)
        self.assertTrue(result)

def _test_validation(name, to_validate):
    rules = SC.ValidationRules(name)
    rules.validate(str(files(XML).joinpath(to_validate)))
    for failure in rules.get_report().failures:
        print(failure)
    for warning in rules.get_report().warnings:
        print(warning)
    report = rules.get_report()
    return report.is_valid, len(rules.get_report().failures), len(rules.get_report().warnings)

def _full_validation(name, to_validate):
    rules = SC.ValidationRules(name)
    rules.validate(str(files(XML).joinpath(to_validate)))
    for failure in rules.get_report().failures:
        print(failure)
    for warning in rules.get_report().warnings:
        print(warning)
    report = rules.get_report()
    return report.is_valid, rules.get_report().failures, rules.get_report().warnings
