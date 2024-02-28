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

from typing import Optional
import unittest

from lxml import etree as ET

from importlib_resources import files
from eark_validator.model.specifications import Specification, Requirement

from eark_validator.specifications.specification import (
    EarkSpecifications,
    Specifications,
    StructuralRequirements)
import tests.resources.xml as XML
from eark_validator.ipxml.resources import profiles

class SpecificationTest(unittest.TestCase):

    def test_no_file(self):
        with self.assertRaises(FileNotFoundError):
            Specifications._from_xml_file(str(files('tests.resources').joinpath('nosuch.file')))

    def test_is_dir(self):
        with self.assertRaises(ValueError):
            Specifications._from_xml_file(str(files(XML)))

    def test_no_xml(self):
        with self.assertRaises(ET.XMLSyntaxError):
            Specifications._from_xml_file(str(files('tests.resources').joinpath('empty.file')))

    def test_invalid_xml(self):
        with self.assertRaises(ET.XMLSyntaxError):
            Specifications._from_xml_file(str(files('tests.resources.xml').joinpath('person.xml')))

    def test_valid_xml(self):
        specification: Specification = Specifications._from_xml_file(str(files(profiles).joinpath('E-ARK-CSIP' + '.xml')))
        self.assertEqual(EarkSpecifications.CSIP.specification, specification)

class StructuralRequirementsTest(unittest.TestCase):

    def test_from_rule_no_none(self):
        with self.assertRaises(ValueError):
            StructuralRequirements.from_rule_no(None)

    def test_from_rule_no_str(self):
        with self.assertRaises(ValueError):
            StructuralRequirements.from_rule_no('1')

    def test_from_rule_no(self):
        req: Requirement = StructuralRequirements.from_rule_no(1)
        self.assertEqual(req.id, 'CSIPSTR1')

class EarkSpecificationsTest(unittest.TestCase):

    def test_title(self):
        spec = EarkSpecifications.CSIP
        self.assertEqual(spec.title, 'E-ARK-CSIP')
        spec = EarkSpecifications.SIP
        self.assertEqual(spec.title, 'E-ARK-SIP')
        spec = EarkSpecifications.DIP
        self.assertEqual(spec.title, 'E-ARK-DIP')

    def test_spec_title(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertEqual(spec.title, 'E-ARK CSIP METS Profile')
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(spec.title, 'E-ARK SIP METS Profile 2.0')
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(spec.title, 'E-ARK DIP METS Profile')

    def test_path(self):
        path = str(files(profiles).joinpath('E-ARK-CSIP' + '.xml'))
        spec = EarkSpecifications.CSIP
        self.assertEqual(spec.path, path)
        path = str(files(profiles).joinpath('E-ARK-SIP' + '.xml'))
        spec = EarkSpecifications.SIP
        self.assertEqual(spec.path, path)
        path = str(files(profiles).joinpath('E-ARK-DIP' + '.xml'))
        spec = EarkSpecifications.DIP
        self.assertEqual(spec.path, path)

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
        self.assertEqual(_count_reqs(spec), spec.requirement_count)
        spec = EarkSpecifications.SIP.specification
        self.assertEqual(_count_reqs(spec), spec.requirement_count)
        spec = EarkSpecifications.DIP.specification
        self.assertEqual(_count_reqs(spec), spec.requirement_count)

    def test_get_requirement(self):
        spec = EarkSpecifications.CSIP.specification
        rule_1 = spec.get_requirement_by_id('CSIP1')
        rule_1_by_sect = spec.get_requirement_by_sect('CSIP1', 'metsRootElement')
        self.assertEqual(rule_1, rule_1_by_sect)
        self.assertIsNone(spec.get_requirement_by_id('CSIP999'))

    def test_sections(self):
        spec = EarkSpecifications.CSIP.specification
        self.assertGreater(len(spec.sections), 0)
        self.assertEqual(_count_reqs(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)
        spec = EarkSpecifications.SIP.specification
        self.assertGreater(len(spec.sections), 0)
        self.assertEqual(_count_reqs(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)
        spec = EarkSpecifications.DIP.specification
        self.assertGreater(len(spec.sections), 0)
        self.assertEqual(_count_reqs(spec), spec.requirement_count)
        self.assertEqual(len(spec.section_requirements()), spec.requirement_count)

def _count_reqs(spec):
    req_count = 0
    for section in spec.sections:
        for _ in spec.section_requirements(section):
            req_count += 1
    return req_count
