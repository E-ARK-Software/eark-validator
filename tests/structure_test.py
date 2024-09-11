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

EXP_NOT_WELLFORMED = 'Expecting status NOTWELLFORMED, not {}'
EXP_WELLFORMED = 'Expecting status WellFormed, not {}'
EXP_ERRORS = 'Expecting {} errors but found {}'
class StructValidationTests(unittest.TestCase):
    """Unit tests covering structural validation of information packages, spcifically
    unpacking archived packages and establishing that the files and folders specified
    if the CSSTRUCT are present."""
    ip_res_root: str = os.path.join(os.path.dirname(__file__), 'resources', 'ips')
    bad_ip_root: str = os.path.join(ip_res_root, 'bad')

    def test_str1_bad_path(self):
        """Test a package that's just a compressed single file."""
        ip_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'empty.file'))
        _, details = STRUCT.validate(ip_path)
        err_count = 1
        self.assertEqual(len(details.errors), err_count,
                        EXP_ERRORS.format(err_count, len(details.errors)))
        self.assertTrue(contains_rule_id(details.errors, 'CSIPSTR1',
                                         severity=Severity.ERROR))

    def test_str1_package_root_single(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(self.bad_ip_root, 'single_file.zip'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NOTWELLFORMED,
                        EXP_NOT_WELLFORMED.format(details.status))
        err_count = 1
        self.assertEqual(len(details.errors), err_count,
                        EXP_ERRORS.format(err_count, len(details.errors)))
        self.assertTrue(contains_rule_id(details.errors, 'CSIPSTR1',
                                         severity=Severity.ERROR))

    def test_str1_package_root_multi_dir(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(self.bad_ip_root, 'multi_dir'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NOTWELLFORMED,
                        EXP_NOT_WELLFORMED.format(details.status))
        err_count = 1
        self.assertEqual(len(details.errors), err_count,
                        EXP_ERRORS.format(err_count, len(details.errors)))
        self.assertTrue(contains_rule_id(details.errors, 'CSIPSTR1',
                                         severity=Severity.ERROR))

    def test_str1_package_root_multi_file(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(self.bad_ip_root, 'multi_file.zip'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NOTWELLFORMED,
                        EXP_NOT_WELLFORMED.format(details.status))
        err_count = 1
        self.assertEqual(len(details.errors), err_count,
                        EXP_ERRORS.format(err_count, len(details.errors)))
        self.assertTrue(contains_rule_id(details.errors, 'CSIPSTR1',
                                         severity=Severity.ERROR))

    def test_str1_package_root_multi_var(self):
        """Dedicated test for package root detection errors."""
        ip_path = Path(os.path.join(self.bad_ip_root, 'multi_var.zip'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NOTWELLFORMED,
                        EXP_NOT_WELLFORMED.format(details.status))
        err_count = 1
        self.assertEqual(len(details.errors), err_count,
                        EXP_ERRORS.format(err_count, len(details.errors)))
        self.assertTrue(contains_rule_id(details.errors, 'CSIPSTR1',
                                         severity=Severity.ERROR))

    def test_str1_single_file_archive(self):
        """Test a package that's just a compressed single file."""
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'empty.zip'))
        _, details = STRUCT.validate(ip_path)
        err_count = 1
        self.assertEqual(len(details.errors), err_count,
                        EXP_ERRORS.format(err_count, len(details.errors)))
        self.assertTrue(contains_rule_id(details.errors, 'CSIPSTR1',
                                         severity=Severity.ERROR))

    def test_no_messages(self):
        """Test package with no METS.xml file"""
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_messages.tar.gz'))
        is_valid, details = STRUCT.validate(ip_path)
        self.assertTrue(is_valid)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_NOT_WELLFORMED.format(details.status))
        self.assertEqual(len(details.messages), 0)

    def test_minimal(self):
        """Test minimal STRUCT with schemas, the basic no errors but with warnings package."""
        ip_path = Path(os.path.join(self.ip_res_root, 'minimal',
                               'minimal_IP_with_schemas.zip'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        self.assertEqual(len(val_warnings), 5,
                        'Expecting 2 warnings but found {}'.format(len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR6',
                                         severity=Severity.WARNING))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR7',
                                         severity=Severity.WARNING))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR12',
                                         severity=Severity.WARNING))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR13',
                                         severity=Severity.WARNING))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR16',
                                         severity=Severity.WARNING))

    def test_str3_package(self):
        """Test minimal STRUCT with schemas, the basic no errors but with warnings package."""
        ip_path = Path(os.path.join(self.ip_res_root, 'unpacked',
                               '733dc055-34be-4260-85c7-5549a7083031'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        self.assertEqual(len(details.warnings), 1,
                        'Expecting 1 warning but found {}'.format(len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR16',
                                         severity=Severity.WARNING))
        self.assertEqual(len(details.infos), 2,
                        'Expecting 2 info messages but found {}'.format(len(details.infos)))
        self.assertTrue(contains_rule_id(details.infos, 'CSIPSTR3',
                                         severity=Severity.INFORMATION))

    def test_str4_nomets(self):
        """Test package with no METS.xml file"""
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_mets.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.NOTWELLFORMED,
                        EXP_NOT_WELLFORMED.format(details.status))
        err_count = 1
        self.assertEqual(len(details.messages), err_count,
                        EXP_ERRORS.format(err_count, len(details.messages)))
        self.assertTrue(contains_rule_id(details.messages, 'CSIPSTR4'))

    def test_str5_nomd(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_md.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR5',
                                         severity=Severity.WARNING))

    def test_str6_nopres(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_pres.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR6',
                                         severity=Severity.WARNING))

    def test_str7_nodesc(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_desc.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR7',
                                         severity=Severity.WARNING))

    def test_str8_noother(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_other.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.infos)))
        self.assertTrue(contains_rule_id(details.infos, 'CSIPSTR8',
                                         severity=Severity.INFORMATION))

    def test_str9_noreps(self):
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_reps.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        val_warnings = details.warnings
        err_count = 1
        self.assertEqual(len(val_warnings), err_count,
                        EXP_ERRORS.format(err_count, len(val_warnings)))
        self.assertTrue(contains_rule_id(val_warnings, 'CSIPSTR9',
                                         severity=Severity.WARNING))

    def test_str10_emptyreps(self):
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'empty_reps.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        err_count = 1
        self.assertEqual(len(details.messages), err_count,
                        EXP_ERRORS.format(err_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR10',
                                         severity=Severity.WARNING))

    def test_str11_nodata(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_data.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR11',
                                         severity=Severity.WARNING))

    def test_str12_norepmets(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_repmets.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR12',
                                         severity=Severity.WARNING))

    def test_str13_norepmd(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_repmd.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR13',
                                         severity=Severity.WARNING))

    def test_str15_noschema(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_schemas.tar.gz'))
        _, details = STRUCT.validate(ip_path)

        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR15',
                                         severity=Severity.WARNING))

    def test_str16_nodocs(self):
        # test as root
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_docs.tar.gz'))
        _, details = STRUCT.validate(ip_path)
        self.assertEqual(details.status, STRUCT.StructureStatus.WELLFORMED,
                        EXP_WELLFORMED.format(details.status))
        warn_count = 1
        self.assertEqual(len(details.messages), warn_count,
                        EXP_ERRORS.format(warn_count, len(details.warnings)))
        self.assertTrue(contains_rule_id(details.warnings, 'CSIPSTR16',
                                         severity=Severity.WARNING))

    def test_get_reps(self):
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_messages.tar.gz'))
        checker: STRUCT.StructureChecker = STRUCT.StructureChecker(ip_path)
        reps_count = 1
        self.assertEqual(len(checker.get_representations()), reps_count,
                        EXP_ERRORS.format(reps_count, len(checker.get_representations())))

    def test_get_no_reps(self):
        ip_path = Path(os.path.join(self.ip_res_root, 'struct',
                               'no_reps.tar.gz'))
        checker: STRUCT.StructureChecker = STRUCT.StructureChecker(ip_path)
        reps_count = 0
        self.assertEqual(len(checker.get_representations()), reps_count,
                        EXP_ERRORS.format(reps_count, len(checker.get_representations())))
