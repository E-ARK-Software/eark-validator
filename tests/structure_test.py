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
# regarding copyright ownershSTRUCT. The E-ARK project licenses
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
"""Module covering tests for package structure errors."""
import os
import unittest
from pathlib import Path

from eark_validator import structure as STRUCT
from eark_validator.model import Severity
from tests.utils_test import contains_rule_id

EXP_NOT_WELLFORMED = 'Expecting status NotWellFormed, not {}'
EXP_WELLFORMED = 'Expecting status WellFormed, not {}'
EXP_ERRORS = 'Expecting {} errors but found {}'
class StructValidationTests(unittest.TestCase):
    """Unit tests covering structural validation of information packages, spcifically
    unpacking archived packages and establishing that the files and folders specified
    if the CSSTRUCT are present."""

    def test_check_package_root_single(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'unpacked',
                               'single_file'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NotWellFormed,
                        EXP_NOT_WELLFORMED.format(details.status))
        val_errors = details.errors
        err_count = 1
        self.assertEqual(len(val_errors), err_count,
                        EXP_ERRORS.format(err_count, len(val_errors)))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR4',
                                         severity=Severity.Error))

    def test_check_package_root_multi_dir(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'unpacked',
                               'multi_dir'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NotWellFormed,
                        EXP_NOT_WELLFORMED.format(details.status))
        val_errors = details.errors
        err_count = 1
        self.assertEqual(len(val_errors), err_count,
                        EXP_ERRORS.format(err_count, len(val_errors)))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR4',
                                         severity=Severity.Error))

    def test_check_package_root_multi_file(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'unpacked',
                               'multi_file'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NotWellFormed,
                        EXP_NOT_WELLFORMED.format(details.status))
        val_errors = details.errors
        err_count = 1
        self.assertEqual(len(val_errors), err_count,
                        EXP_ERRORS.format(err_count, len(val_errors)))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR4',
                                         severity=Severity.Error))

    def test_check_package_root_multi_var(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'unpacked',
                               'multi_var'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NotWellFormed,
                        EXP_NOT_WELLFORMED.format(details.status))
        val_errors = details.errors
        err_count = 1
        self.assertEqual(len(val_errors), err_count,
                        EXP_ERRORS.format(err_count, len(val_errors)))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR4',
                                         severity=Severity.Error))

    def test_single_file_archive(self):
        """Test a package that's just a compressed single file."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'empty.zip'))
        _, details = STRUCT.validate(ip_path)
        val_errors = details.errors
        err_count = 1
        self.assertEqual(len(val_errors), err_count,
                        EXP_ERRORS.format(err_count, len(val_errors)))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR1',
                                         severity=Severity.Error))

    def test_minimal(self):
        """Test minimal STRUCT with schemas, the basic no errors but with warnings package."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'minimal',
                               'minimal_IP_with_schemas.zip'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WellFormed,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        self.assertEqual(len(val_warnings), 3,
                        'Expecting 2 warnings but found {}'.format(len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR6',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR7',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR16',
                                         severity=Severity.Warning))

    def test_nomets(self):
        """Test package with no METS.xml file"""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'no_mets.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NotWellFormed,
                        EXP_NOT_WELLFORMED.format(details.status))
        val_errors = details.errors
        err_count = 1
        self.assertEqual(len(val_errors), err_count,
                        EXP_ERRORS.format(err_count, len(val_errors)))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR4'))

        val_warnings = details.warnings
        self.assertEqual(len(val_warnings), 3,
                        'Expecting 2 warnings but found {}'.format(len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR6',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR7',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR16',
                                         severity=Severity.Warning))

    def test_nomd(self):
        # test as root
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'no_md.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WellFormed,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        warn_count = 4
        self.assertEqual(len(val_warnings), warn_count,
                        EXP_ERRORS.format(warn_count, len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR5',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR6',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR7',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR16',
                                         severity=Severity.Warning))

    def test_noschema(self):
        # test as root
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'no_schemas.tar.gz'))
        _, details = STRUCT.validate(ip_path)

        self.assertEqual(details.status, STRUCT.StructureStatus.WellFormed,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        warn_count = 4
        self.assertEqual(len(val_warnings), warn_count,
                        EXP_ERRORS.format(warn_count, len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR6',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR7',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR15',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR16',
                                         severity=Severity.Warning))

    def test_nodata(self):
        # test as root
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'no_data.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WellFormed,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        warn_count = 3
        self.assertEqual(len(val_warnings), warn_count,
                        EXP_ERRORS.format(warn_count, len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR6',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR7',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR16',
                                         severity=Severity.Warning))

    def test_noreps(self):
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'no_reps.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WellFormed,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        err_count = 4
        self.assertEqual(len(val_warnings), err_count,
                        EXP_ERRORS.format(err_count, len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR9',
                                         severity=Severity.Warning))
    """Unit tests covering structural validation of information packages, spcifically
    unpacking archived packages and establishing that the files and folders specified
    if the CSIP are present."""

class StructManifestValidationTests():
    def test_manifest_nomets(self):
        """Ensure proper behaviour when no METS file is present."""
        # test as root
        man_no_mets = STRUCT.StructureChecker(Path(os.path.join(os.path.dirname(__file__), 'resources', 'ips', 'struct',
                               'no_mets.tar.gz')))
        val_errors = man_no_mets.validate_manifest()
        self.assertEqual(len(val_errors), 1)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR4'))
        val_errors = man_no_mets.validate_manifest(is_root=False)
        self.assertEqual(len(val_errors), 2)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR12',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR11',
                                         severity=Severity.Warning))

    def test_manifest_nomd(self):
        # test as root
        man_no_md = STRUCT.StructureChecker('no_md')
        val_errors = man_no_md.validate_manifest()
        self.assertEqual(len(val_errors), 1)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR5',
                                         severity=Severity.Warning))
        val_errors = man_no_md.validate_manifest(is_root=False)
        self.assertEqual(len(val_errors), 2)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR13',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR11',
                                         severity=Severity.Warning))

    def test_manifest_noschema(self):
        # test as root
        man_no_schema = STRUCT.StructureChecker('no_schema')
        val_errors = man_no_schema.validate_manifest()
        self.assertEqual(len(val_errors), 1)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR15',
                                         severity=Severity.Warning))
        val_errors = man_no_schema.validate_manifest(is_root=False)
        self.assertEqual(len(val_errors), 2)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR15',
                                         severity=Severity.Warning))
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR11',
                                         severity=Severity.Warning))

    def test_manifest_data(self):
        # test as root
        man_data = STRUCT.StructureChecker('data')
        val_errors = man_data.validate_manifest()
        self.assertEqual(len(val_errors), 0)
        val_errors = man_data.validate_manifest(is_root=False)
        self.assertEqual(len(val_errors), 0)

    def test_manifest_noreps(self):
        man_no_reps = STRUCT.StructureChecker('no_reps')
        val_errors = man_no_reps.validate_manifest()
        self.assertEqual(len(val_errors), 1)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR9',
                                         severity=Severity.Warning))
        val_errors = man_no_reps.validate_manifest(is_root=False)
        self.assertEqual(len(val_errors), 1)
        self.assertTrue(contains_rule_id(val_errors, 'CSIPSTR11',
                                         severity=Severity.Warning))
