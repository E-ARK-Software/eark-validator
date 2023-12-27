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

from lxml import etree as ET

from importlib_resources import files

from eark_validator.specifications.specification import EarkSpecifications
from eark_validator.specifications.specification import Specification
import tests.resources.xml as XML



class SpecificationTest(unittest.TestCase):

    def test_no_file(self):
        with self.assertRaises(FileNotFoundError):
            Specification._from_xml_file(str(files('tests.resources').joinpath('nosuch.file')))

    def test_is_dir(self):
        with self.assertRaises(ValueError):
            Specification._from_xml_file(str(files(XML)))

    def test_no_xml(self):
        with self.assertRaises(ET.XMLSyntaxError):
            Specification._from_xml_file(str(files('tests.resources').joinpath('empty.file')))

    def test_invalid_xml(self):
        with self.assertRaises(ET.XMLSyntaxError):
            Specification._from_xml_file(str(files('tests.resources.xml').joinpath('person.xml')))

    def test_title(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertEqual(spec.title, 'E-ARK CSIP METS Profile')
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(spec.title, 'E-ARK SIP METS Profile 2.0')
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(spec.title, 'E-ARK DIP METS Profile')

    def test_url(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertEqual(spec.url, 'https://earkcsip.dilcis.eu/profile/E-ARK-CSIP.xml')
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(spec.url, 'https://earksip.dilcis.eu/profile/E-ARK-SIP.xml')
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(spec.url, 'https://earkdip.dilcis.eu/profile/E-ARK-DIP.xml')

    def test_version(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertEqual(spec.version, 'V2.0.4')
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(spec.version, 'SIPV2.0.4')
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(spec.version, 'DIPV2.0.4')

    def test_date(self):
        spec_date = '2020-06-12T09:00:00'
        spec = EarkSpecifications.CSIP.specification
        self.assertEqual(spec.date, spec_date)
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(spec.date, spec_date)
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(spec.date, spec_date)

    def test_requirements(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertEqual(self._count_reqs(spec), spec.requirement_count)
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(self._count_reqs(spec), spec.requirement_count)
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(self._count_reqs(spec), spec.requirement_count)

    def test_get_requirement(self):
        spec = EarkSpecifications.CSIP.specification
        rule_1 = spec.get_requirement_by_id('CSIP1')
        rule_1_by_sect = spec.get_requirement_by_sect('CSIP1', 'metsRootElement')
        self.assertEqual(rule_1, rule_1_by_sect)
        self.assertIsNone(spec.get_requirement_by_id('CSIP999'))

    def test_sections(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertGreater(spec.section_count, 0)
        self.assertEqual(self._count_reqs_via_section(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)
        spec = EarkSpecifications.SIP.specification
        self.assertGreater(spec.section_count, 0)
        self.assertEqual(self._count_reqs_via_section(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)
        spec = EarkSpecifications.DIP.specification
        self.assertGreater(spec.section_count, 0)
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
