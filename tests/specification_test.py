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
from eark_validator.model.specifications import Specification, StructuralRequirement

from eark_validator.specifications.specification import EarkSpecification, Specifications, StructuralRequirements, SpecificationType, SpecificationVersion
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
        specification: Specification = Specifications._from_xml_file(str(files(profiles).joinpath('V2.0.4', 'E-ARK-CSIP' + '.xml')))
        self.assertEqual(EarkSpecification(SpecificationType.CSIP, SpecificationVersion.V2_0_4).specification, specification)

class StructuralRequirementsTest(unittest.TestCase):

    def test_from_rule_no_none(self):
        with self.assertRaises(ValueError):
            StructuralRequirements.from_rule_no(None)

    def test_from_rule_no_str(self):
        with self.assertRaises(ValueError):
            StructuralRequirements.from_rule_no('1')

    def test_from_rule_no(self):
        req: StructuralRequirement = StructuralRequirements.from_rule_no(1)
        self.assertEqual(req.id, 'CSIPSTR1')

class SpecificationTypeTest(unittest.TestCase):
    def test_value(self):
        type = SpecificationType.CSIP
        self.assertEqual(type.value, 'E-ARK-CSIP')
        type = SpecificationType.SIP
        self.assertEqual(type.value, 'E-ARK-SIP')
        type = SpecificationType.DIP
        self.assertEqual(type.value, 'E-ARK-DIP')

class SpecificationVersionTest(unittest.TestCase):
    def test_value(self):
        version = SpecificationVersion.V2_0_4
        self.assertEqual(version.value, 'V2.0.4')
        version = SpecificationVersion.V2_1_0
        self.assertEqual(version.value, 'V2.1.0')

class EarkSpecificationsTest(unittest.TestCase):
    def test_specifiction_type(self):
        eark_specification = EarkSpecification(SpecificationType.CSIP, SpecificationVersion.V2_0_4)
        self.assertEqual(eark_specification.type, SpecificationType.CSIP)
        eark_specification = EarkSpecification(SpecificationType.SIP, SpecificationVersion.V2_0_4)
        self.assertEqual(eark_specification.type, SpecificationType.SIP)
        eark_specification = EarkSpecification(SpecificationType.DIP, SpecificationVersion.V2_0_4)
        self.assertEqual(eark_specification.type, SpecificationType.DIP)

    def test_specifiction_version(self):
        eark_specification = EarkSpecification(SpecificationType.CSIP, SpecificationVersion.V2_0_4)
        self.assertEqual(eark_specification.version, SpecificationVersion.V2_0_4)
        eark_specification = EarkSpecification(SpecificationType.SIP, SpecificationVersion.V2_1_0)
        self.assertEqual(eark_specification.version, SpecificationVersion.V2_1_0)
