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
"""Module containing tests covering the manifest class."""
import unittest

from ip_validation.infopacks import structure as STRUCT
from ip_validation.infopacks.rules import Severity
from tests.utils import contains_rule_id

class ManifestClassTests(unittest.TestCase):
    """Unit tests covering structural validation of information packages, spcifically
    unpacking archived packages and establishing that the files and folders specified
    if the CSIP are present."""

    def test_manifest_nomets(self):
        """Ensure proper behaviour when no METS file is present."""
        # test as root
        man_no_mets = STRUCT.StructureChecker("no_mets", has_mets=False)
        val_errors = man_no_mets.validate_manifest()
        self.assertTrue(len(val_errors) == 1)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR4"))
        val_errors = man_no_mets.validate_manifest(is_root=False)
        self.assertTrue(len(val_errors) == 2)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR12",
                                         severity=Severity.WRN))
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR11",
                                         severity=Severity.WRN))

    def test_manifest_nomd(self):
        # test as root
        man_no_md = STRUCT.StructureChecker("no_md", has_md=False)
        val_errors = man_no_md.validate_manifest()
        self.assertTrue(len(val_errors) == 1)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR5",
                                         severity=Severity.WRN))
        val_errors = man_no_md.validate_manifest(is_root=False)
        self.assertTrue(len(val_errors) == 2)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR13",
                                         severity=Severity.WRN))
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR11",
                                         severity=Severity.WRN))

    def test_manifest_noschema(self):
        # test as root
        man_no_schema = STRUCT.StructureChecker("no_schema", has_schema=False)
        val_errors = man_no_schema.validate_manifest()
        self.assertTrue(len(val_errors) == 1)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR15",
                                         severity=Severity.WRN))
        val_errors = man_no_schema.validate_manifest(is_root=False)
        self.assertTrue(len(val_errors) == 2)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR15",
                                         severity=Severity.WRN))
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR11",
                                         severity=Severity.WRN))

    def test_manifest_data(self):
        # test as root
        man_data = STRUCT.StructureChecker("data", has_data=True)
        val_errors = man_data.validate_manifest()
        self.assertTrue(len(val_errors) == 0)
        val_errors = man_data.validate_manifest(is_root=False)
        self.assertTrue(len(val_errors) == 0)

    def test_manifest_noreps(self):
        man_no_reps = STRUCT.StructureChecker("no_reps", has_reps=False)
        val_errors = man_no_reps.validate_manifest()
        self.assertTrue(len(val_errors) == 1)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR9",
                                         severity=Severity.WRN))
        val_errors = man_no_reps.validate_manifest(is_root=False)
        self.assertTrue(len(val_errors) == 1)
        self.assertTrue(contains_rule_id(val_errors, "CSIPSTR11",
                                         severity=Severity.WRN))
