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
"""Module to capture everything schematron validation related."""
import os
from importlib_resources import files
from typing import Generator

from lxml import etree as ET
from lxml.isoschematron import Schematron

from .resources import schematron as SCHEMATRON
from ip_validation.const import NO_PATH, NOT_FILE

SCHEMATRON_NS = "{http://purl.oclc.org/dsdl/schematron}"
SVRL_NS = "{http://purl.oclc.org/dsdl/svrl}"

class SchematronRuleset():
    """Encapsulates a set of Schematron rules loaded from a file."""
    def __init__(self, sch_path: str=None):
        if not os.path.exists(sch_path):
            raise FileNotFoundError(NO_PATH.format(sch_path))
        if not os.path.isfile(sch_path):
            raise ValueError(NOT_FILE.format(sch_path))
        self._path = sch_path
        try:
            self._schematron = Schematron(file=self._path, store_schematron=True, store_report=True)
        except ET.SchematronParseError as ex:
            raise ValueError('Rules file is not valid XML: {}. {}'.format(sch_path, ex.error_log.last_error.message ))
        except KeyError as ex:
            raise ValueError('Rules file is not valid Schematron: {}. {}'.format(sch_path, ex.__doc__))

    @property
    def path(self) -> str:
        """Return the path to the Schematron rules file."""
        return self._path

    @property
    def schematron(self) -> Schematron:
        """Return the Schematron object."""
        return self._schematron

    def get_assertions(self) -> Generator[ ET.Element, None, None]:
        """Generator that returns the rules one at a time."""
        xml_rules = ET.XML(bytes(self.schematron.schematron))
        for ele in xml_rules.iter():
            if ele.tag == SCHEMATRON_NS + 'assert':
                yield ele

    def validate(self, to_validate: str) -> ET.Element:
        """Validate a file against the loaded Schematron ruleset."""
        xml_file = ET.parse(to_validate)
        self.schematron.validate(xml_file)
        return self.schematron.validation_report
    
def get_schematron_path(id: str, section: str) -> str:
    return str(files(SCHEMATRON).joinpath(id).joinpath('mets_{}_rules.xml'.format(section)))
