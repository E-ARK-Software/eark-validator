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

from ip_validation.infopacks import rules as SC
from ip_validation.infopacks.specification import EarkSpecifications
import tests.resources.schematron as SCHEMATRON
import tests.resources.xml as XML

PERSON_PATH = str(files(SCHEMATRON).joinpath('person.xml'))
NOT_FOUND_PATH = str(files(SCHEMATRON).joinpath('not-found.xml'))
EMPTY_FILE_PATH = str(files('tests.resources').joinpath('empty.file'))
METS_VALID = 'METS-valid.xml'
METS_VALID_PATH = str(files(XML).joinpath(METS_VALID))
METS_ONE_DEF = str(files(SCHEMATRON).joinpath('METS-one-default-ns.xml'))
METS_ROOT_RULES = 'metsRootElement'
METS_HDR_RULES = 'metsHdr'
METS_AMD_RULES = 'amdSec'
METS_DMD_RULES = 'dmdSec'
METS_FILE_RULES = 'fileSec'
METS_STRUCT_RULES = 'structMap'
class ValidationRulesTest(unittest.TestCase):
    """Tests for Schematron validation rules."""
    @classmethod
    def setUpClass(cls):
        cls._person_rules = SC.SchematronRuleset(PERSON_PATH)
        cls._mets_one_def_rules = SC.SchematronRuleset(METS_ONE_DEF)

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
            SC.SchematronRuleset(str(files(XML).joinpath('person.xml')))

    def test_load_schematron(self):
        assert_count = 0
        for _ in self._person_rules.get_assertions():
            assert_count += 1
        self.assertTrue(assert_count > 0)

    def test_validate_person(self):
        self._person_rules.validate(str(files(XML).joinpath('person.xml')))
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

    def test_mets_root(self):
        result, failures, _, _ = _test_validation(METS_ROOT_RULES, METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(result)

    def test_mets_root_no_objid(self):
        result, failures, _, _ = _test_validation(METS_ROOT_RULES, 'METS-no-objid.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_no_type(self):
        result, failures, _, _ = _test_validation(METS_ROOT_RULES, 'METS-no-type.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_other_type(self):
        result, failures, _, _ = _test_validation(METS_ROOT_RULES, 'METS-other-type.xml')
        self.assertTrue(failures == 0)
        self.assertTrue(result)

    def test_mets_root_no_profile(self):
        result, failures, _, _ = _test_validation(METS_ROOT_RULES, 'METS-no-profile.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_no_hdr(self):
        result, failures, _, _ = _test_validation(METS_ROOT_RULES, 'METS-no-hdr.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_hdr_valid(self):
        result, failures, _, _ = _test_validation(METS_HDR_RULES, METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(result)

    def test_mets_hdr_no_createdate(self):
        result, failures, _, _ = _test_validation(METS_HDR_RULES, 'METS-no-createdate.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_file_ownerid(self):
        result, errors, _, infos = _test_validation(METS_FILE_RULES, 'METS-ownerid.xml')
        self.assertTrue(infos == 1)
        self.assertTrue(result)

    def test_mets_hdr_no_type(self):
        result, failures, _, _ = _test_validation(METS_HDR_RULES, 'METS-hdr-no-type.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_hdr_no_version(self):
        result, failures, _, _ = _test_validation(METS_HDR_RULES, 'METS-hdr-no-version.xml')
        self.assertTrue(failures == 1)
        self.assertFalse(result)

    def test_mets_root_dmd(self):
        result, _, warnings = _full_validation(METS_ROOT_RULES, METS_VALID)
        found_csip17 = False
        for warning in warnings:
            if warning.rule_id == 'CSIP17':
                found_csip17 = True
        self.assertTrue(found_csip17)
        self.assertTrue(result)

    def test_mets_dmd(self):
        result, failures, warnings, _ = _test_validation(METS_DMD_RULES, METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 0)
        self.assertTrue(result)

    def test_mets_amd(self):
        result, failures, warnings, _ = _test_validation(METS_AMD_RULES, METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 0)
        self.assertTrue(result)

    def test_mets_file(self):
        result, failures, warnings, _ = _test_validation(METS_FILE_RULES, METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 0)
        self.assertTrue(result)

    def test_mets_structmap(self):
        result, failures, warnings, _ = _test_validation(METS_STRUCT_RULES, METS_VALID)
        self.assertTrue(failures == 0)
        self.assertTrue(warnings == 1)
        self.assertTrue(result)

class ValidationProfileTest(unittest.TestCase):
    def test_load_by_str(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        self.assertEqual(profile.specification.url, 'https://earkcsip.dilcis.eu/profile/E-ARK-CSIP.xml')
        profile = SC.ValidationProfile.from_specification('SIP')
        self.assertEqual(profile.specification.url, 'https://earksip.dilcis.eu/profile/E-ARK-SIP.xml')
        profile = SC.ValidationProfile.from_specification('DIP')
        self.assertEqual(profile.specification.url, 'https://earkdip.dilcis.eu/profile/E-ARK-DIP.xml')

    def test_load_by_eark_spec(self):
        profile = SC.ValidationProfile.from_specification(EarkSpecifications.CSIP)
        self.assertEqual(profile.specification.url, 'https://earkcsip.dilcis.eu/profile/E-ARK-CSIP.xml')
        profile = SC.ValidationProfile.from_specification(EarkSpecifications.SIP)
        self.assertEqual(profile.specification.url, 'https://earksip.dilcis.eu/profile/E-ARK-SIP.xml')
        profile = SC.ValidationProfile.from_specification(EarkSpecifications.DIP)
        self.assertEqual(profile.specification.url, 'https://earkdip.dilcis.eu/profile/E-ARK-DIP.xml')

    def test_load_by_spec(self):
        profile = SC.ValidationProfile.from_specification(EarkSpecifications.CSIP.specification)
        self.assertEqual(profile.specification.url, 'https://earkcsip.dilcis.eu/profile/E-ARK-CSIP.xml')
        profile = SC.ValidationProfile.from_specification(EarkSpecifications.SIP.specification)
        self.assertEqual(profile.specification.url, 'https://earksip.dilcis.eu/profile/E-ARK-SIP.xml')
        profile = SC.ValidationProfile.from_specification(EarkSpecifications.DIP.specification)
        self.assertEqual(profile.specification.url, 'https://earkdip.dilcis.eu/profile/E-ARK-DIP.xml')

    def test_bad_value(self):
        with self.assertRaises(ValueError):
            SC.ValidationProfile.from_specification('BAD')

    def test_valid(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath(METS_VALID)))
        self.assertTrue(profile.is_valid)

    def test_invalid(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath('METS-no-hdr.xml')))
        self.assertFalse(profile.is_valid)

    def test_validate_file_not_found(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        with self.assertRaises(FileNotFoundError):
            profile.validate(str(files(SCHEMATRON).joinpath('not-found.xml')))

    def test_validate_dir_value_err(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        with self.assertRaises(ValueError):
            profile.validate(str(files(SCHEMATRON)))

    def test_validate_empty_file(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources').joinpath('empty.file')))
        self.assertFalse(profile.is_valid)

    def test_validate_not_mets(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath('person.xml')))
        self.assertFalse(profile.is_valid)

    def test_validate_json(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources').joinpath('aip.json')))
        self.assertFalse(profile.is_valid)

    def test_get_results(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath(METS_VALID)))
        self.assertTrue(profile.is_valid)
        self.assertTrue(len(profile.get_results()) == 8)

    def test_get_result(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath(METS_VALID)))
        result = profile.get_result('metsHdr')
        self.assertTrue(profile.is_valid)
        self.assertEqual(len(result.warnings), 1)

    def test_get_bad_key(self):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath(METS_VALID)))
        result = profile.get_result('badkey')
        self.assertIsNone(result)

class SeverityTest(Enum):
    NOT_SEV: 'NOT_SEV'

class ResultTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        profile = SC.ValidationProfile.from_specification('CSIP')
        profile.validate(str(files('tests.resources.xml').joinpath(METS_VALID)))
        cls._result = profile.get_result('metsHdr').warnings[0]

    def test_get_message(self):
        self.assertIsNotNone(self._result.message)

    def test_sev_instances(self):
        for sev in SC.Severity:
            self._result.severity = sev

    def test_sev_names(self):
        for sev in SC.Severity:
            self._result.severity = sev.name

    def test_sev_values(self):
        for sev in SC.Severity:
            self._result.severity = sev.value

    def test_bad_sev_string(self):
        with self.assertRaises(ValueError):
            self._result.severity = 'BAD'

    def test_bad_sev_att(self):
        with self.assertRaises(AttributeError):
            self._result.severity = SeverityTest.NOT_SEV

def _test_validation(name, to_validate):
    rules = SC.SchematronRuleset(SC.get_schematron_path('CSIP', name))
    rules.validate(str(files(XML).joinpath(to_validate)))
    for failure in SC.TestReport.from_validation_report(rules._schematron.validation_report).errors:
        print(failure)
    for warning in SC.TestReport.from_validation_report(rules._schematron.validation_report).warnings:
        print(warning)
    report = SC.TestReport.from_validation_report(rules._schematron.validation_report)
    return report.is_valid, len(report.errors), len(report.warnings), len(report.infos)

def _full_validation(name, to_validate):
    rules = SC.SchematronRuleset(SC.get_schematron_path('CSIP', name))
    rules.validate(str(files(XML).joinpath(to_validate)))
    for failure in SC.TestReport.from_validation_report(rules._schematron.validation_report).errors:
        print(failure)
    for warning in SC.TestReport.from_validation_report(rules._schematron.validation_report).warnings:
        print(warning)
    report = SC.TestReport.from_validation_report(rules._schematron.validation_report)
    return report.is_valid, report.errors, report.warnings
