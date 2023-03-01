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

from ip_validation.infopacks.specification import EarkSpecifications as SPEC

class SpecificationTest(unittest.TestCase):

    def test_title(self):
        spec = SPEC.CSIP.specification
        self.assertEqual(spec.title, 'E-ARK CSIP METS Profile')
        spec = SPEC.SIP.specification
        self.assertEqual(spec.title, 'E-ARK SIP METS Profile 2.0')
        spec = SPEC.DIP.specification
        self.assertEqual(spec.title, 'E-ARK DIP METS Profile')

    def test_version(self):
        spec = SPEC.CSIP.specification
        self.assertEqual(spec.version, 'V2.0.4')
        spec = SPEC.SIP.specification
        self.assertEqual(spec.version, 'SIPV2.0.4')
        spec = SPEC.DIP.specification
        self.assertEqual(spec.version, 'DIPV2.0.4')

    def test_date(self):
        spec_date = '2020-06-12T09:00:00'
        spec = SPEC.CSIP.specification
        self.assertEqual(spec.date, spec_date)
        spec = SPEC.SIP.specification
        self.assertEqual(spec.date, spec_date)
        spec = SPEC.DIP.specification
        self.assertEqual(spec.date, spec_date)

    def test_requirements(self):
        spec = SPEC.CSIP.specification
        self.assertEqual(self._count_reqs(spec), spec.requirement_count)
        spec = SPEC.SIP.specification
        self.assertEqual(self._count_reqs(spec), spec.requirement_count)
        spec = SPEC.DIP.specification
        self.assertEqual(self._count_reqs(spec), spec.requirement_count)

    def test_sections(self):
        spec = SPEC.CSIP.specification
        self.assertTrue(spec.section_count > 0)
        self.assertEqual(self._count_reqs_via_section(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)
        spec = SPEC.SIP.specification
        self.assertTrue(spec.section_count > 0)
        self.assertEqual(self._count_reqs_via_section(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)
        spec = SPEC.DIP.specification
        self.assertTrue(spec.section_count > 0)
        self.assertEqual(self._count_reqs_via_section(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)

    def _count_reqs(self, spec):
        req_count = 0
        for _ in spec.requirements:
            req_count += 1
        return req_count

    def _count_reqs_via_section(self, spec):
        req_count = 0
        for section in spec.sections:
            for _ in spec.section_requirements(section):
                req_count += 1
        return req_count