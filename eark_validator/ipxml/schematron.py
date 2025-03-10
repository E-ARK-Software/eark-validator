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
"""Module to capture everything schematron validation related."""
import os
from urllib.request import urlopen
from typing import Generator
from pathlib import Path
from typing import Optional

from importlib_resources import files

from lxml import etree as ET
from pyschematron import validate_document, ValidationResult

from eark_validator.const import NO_PATH, NOT_FILE
from .resources import schematron as SCHEMATRON

SCHEMATRON_NS = '{http://purl.oclc.org/dsdl/schematron}'
SVRL_NS = '{http://purl.oclc.org/dsdl/svrl}'

class SchematronTests():
    __vocabulary_definitions = {
        '@TYPE': 'https://earkcsip.dilcis.eu/schema/CSIPVocabularyContentCategory.xml',
        '@csip:CONTENTINFORMATIONTYPE': 'https://earkcsip.dilcis.eu/schema/CSIPVocabularyContentInformationType.xml',
        '@csip:OAISPACKAGETYPE': 'https://earkcsip.dilcis.eu/schema/CSIPVocabularyOAISPackageType.xml',
        '@STATUS': 'https://earkcsip.dilcis.eu/schema/CSIPVocabularyStatus.xml',
        '@USE': 'https://earkcsip.dilcis.eu/schema/CSIPVocabularyFileGrpAndStructMapDivisionLabel.xml'
    }

    tests = {}

    def __init__(self, to_validate: Optional[Path]):
        for attribute, vocabulary_uri in self.__vocabulary_definitions.items():
            self.tests[attribute + '_vocabulary_test'] = self._create_vocabulary_test(attribute, vocabulary_uri)

        if to_validate:
            self.tests["@OBJID_test"] = self._create_OBJID_test(to_validate)

    def _create_vocabulary_test(self, attribute: str, vocabulary_uri: str) -> str:
        vocabulary_tests = []
        for line_bytes in urlopen(vocabulary_uri):
            line = line_bytes.decode('utf-8')
            if 'Term' not in line:
                continue

            start = line.find('>') + 1
            end = line.find('<', start)

            vocabulary_item = line[start:end]
            vocabulary_tests.append(f"({attribute} = '{vocabulary_item}')")

        return ' or '.join(vocabulary_tests)
    
    def _create_OBJID_test(self, to_validate: Path):
        return f"(@OBJID = '{to_validate.stem}')"

class SchematronRuleset():
    """Encapsulates a set of Schematron rules loaded from a file."""
    def __init__(self, sch_path: str=None, to_validate: Path=None):
        if not os.path.exists(sch_path):
            raise FileNotFoundError(NO_PATH.format(sch_path))
        if not os.path.isfile(sch_path):
            raise ValueError(NOT_FILE.format(sch_path))
        self._path = sch_path

        schematron_tests = SchematronTests(to_validate)
        try:
            with open(sch_path) as schematron_file:
                schematron_data = schematron_file.read()
                for test_name, test_value in schematron_tests.tests.items():
                    schematron_data = schematron_data.replace(test_name, test_value)

                self.schematron_tree = ET.ElementTree(ET.fromstring(schematron_data))
        except Exception as ex:
            ex_mess = ex.__doc__
            raise ValueError(f'Rules file is not valid Schematron: {sch_path}. {ex_mess}') from ex

    @property
    def path(self) -> str:
        """Return the path to the Schematron rules file."""
        return self._path

    @property
    def result(self) -> Optional[ValidationResult]:
        """Return the validation result."""
        return self.validation_result

    def validate(self, to_validate: str) -> ET._ElementTree:
        """Validate a file against the loaded Schematron ruleset."""
        xml_path = Path(to_validate)
        self.validation_result = validate_document(xml_path, self.schematron_tree)
        return self.result.get_svrl()

def get_schematron_path(version: str, spec_id: str, section: str) -> str:
    return str(files(SCHEMATRON).joinpath(version).joinpath(spec_id).joinpath(f'mets_{section}_rules.xml'))
