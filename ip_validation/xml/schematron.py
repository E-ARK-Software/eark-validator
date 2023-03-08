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

from lxml import etree as ET
from lxml.isoschematron import Schematron

from importlib_resources import files

from ip_validation.xml import SCHEMATRON
from ip_validation.const import NO_PATH, NOT_FILE

SCHEMATRON_NS = "{http://purl.oclc.org/dsdl/schematron}"
SVRL_NS = "{http://purl.oclc.org/dsdl/svrl}"

class SchematronRuleset():
    """Encapsulates a set of Schematron rules loaded from a file."""
    def __init__(self, specification, section, rules_path=None):
        self._specification = specification
        self._section = section
        if not rules_path:
            rules_path = str(files(SCHEMATRON).joinpath(specification).joinpath('mets_{}_rules.xml'.format(section)))
        if not os.path.exists(rules_path):
            raise FileNotFoundError(NO_PATH.format(rules_path))
        if not os.path.isfile(rules_path):
            raise ValueError(NOT_FILE.format(rules_path))
        self.rules_path = rules_path
        try:
            self.ruleset = Schematron(file=self.rules_path, store_schematron=True, store_report=True)
        except ET.SchematronParseError as ex:
            raise ValueError('Rules file is not valid XML: {}. {}'.format(rules_path, ex.error_log.last_error.message ))
        except KeyError as ex:
            raise ValueError('Rules file is not valid Schematron: {}. {}'.format(rules_path, ex.__doc__))

    @property
    def specification(self):
        """Get the specification ID."""
        return self._specification

    @property
    def section(self):
        """Get the specification section name."""
        return self._section

    def get_assertions(self):
        """Generator that returns the rules one at a time."""
        xml_rules = ET.XML(bytes(self.ruleset.schematron))

        for ele in xml_rules.iter():
            if ele.tag == SCHEMATRON_NS + 'assert':
                yield ele

    def validate(self, to_validate):
        """Validate a file against the loaded Schematron ruleset."""
        xml_file = ET.parse(to_validate)
        self.ruleset.validate(xml_file)
