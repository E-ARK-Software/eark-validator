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
from enum import Enum, unique
import logging

import lxml.etree
from lxml.isoschematron import Schematron

from importlib_resources import files

import ip_validation.resources.schematron

class ValidationRules():
    """Encapsulates a set of Schematron rules loaded from a file."""
    def __init__(self, name, rules_path=None):
        self.name = name
        if not rules_path:
            rules_path = 'mets_{}_rules.xml'.format(name)
        self.rules_path = str(files(ip_validation.resources.schematron).joinpath(rules_path))
        logging.debug("path: %s", self.rules_path)
        self.ruleset = Schematron(file=self.rules_path, store_schematron=True, store_report=True)

    def get_rules(self):
        """Returns the loaded Schematron ruleset."""
        return self.ruleset.schematron

    def validate(self, to_validate):
        """Validate a file against the loaded Schematron ruleset."""
        xml_file = lxml.etree.parse(to_validate)
        return self.ruleset.validate(xml_file)

    def get_report(self):
        """Get the report from the last validation."""
        return self.ruleset.validation_report

class ValidationProfile():
    """ A complete set of Schematron rule sets that comprise a complete validation profile."""
    def __init__(self):
        self.rulesets = {}
        self.results = {}
        self.rulesets['root'] = ValidationRules("root", "mets_root_rules.xml")
        self.rulesets['hdr'] = ValidationRules("hdr", "mets_hdr_rules.xml")
        self.rulesets['amd'] = ValidationRules("amd", "mets_amd_rules.xml")
        self.rulesets['dmd'] = ValidationRules("dmd", "mets_dmd_rules.xml")
        self.rulesets['file'] = ValidationRules("file", "mets_file_rules.xml")
        self.rulesets['structmap'] = ValidationRules("structmap", "mets_structmap_rules.xml")

    def validate(self, to_validate):
        """Validates a file against each loaded ruleset."""
        self.results['root'] = self.rulesets['root'].validate(to_validate)
        self.results['hdr'] = self.rulesets['hdr'].validate(to_validate)
        self.results['amd'] = self.rulesets['amd'].validate(to_validate)
        self.results['dmd'] = self.rulesets['dmd'].validate(to_validate)
        self.results['file'] = self.rulesets['file'].validate(to_validate)
        self.results['structmap'] = self.rulesets['structmap'].validate(to_validate)

    def get_results(self):
        """Return the full set of results."""
        return self.results

    def get_result(self, name):
        """Return onlyt the results for element name."""
        return self.results.get(name)

@unique
class Severity(Enum):
    """Enum covering information package validation statuses."""
    Unknown = 1
    # Information level, possibly not best practise
    Info = 2
    # Non-fatal issue that should be corrected
    Warn = 3
    # Error level message means invalid package
    Error = 4

class TestResult():
    """Encapsulates an individual validation test result."""
    def __init__(self, rule_id, location, message, severity):
        self._rule_id = rule_id
        self._severity = severity
        self._location = location
        self._message = message

    @property
    def rule_id(self):
        """Get the rule_id."""
        return self._rule_id

    @property
    def severity(self):
        """Get the severity."""
        return self._severity

    @severity.setter
    def severity(self, value):
        if not value in list(Severity):
            raise ValueError("Illegal severity value")
        self._severity = value

    @property
    def location(self):
        """Get the location location."""
        return self._location

    @property
    def message(self):
        """Get the message."""
        return self._message

    @classmethod
    def from_element(cls, rule, failed_assert, severity=Severity.Error):
        """Create a Test result from an element."""
        rule_id = rule.get('id')
        context = rule.get('context')
        test = failed_assert.get('test')
        location = failed_assert.get('location')
        message = failed_assert.find('{http://purl.oclc.org/dsdl/svrl}text').text
        schmtrn_loc = SchematronLocation(context, test, location)
        return cls(rule_id, schmtrn_loc, message, severity)

    @classmethod
    def from_element_warn(cls, rule, failed_assert):
        """Create a warning from an element."""
        return cls.from_element(rule, failed_assert, Severity.Warn)

class SchematronLocation():
    """All details of the location of a Schematron error."""
    def __init__(self, context, test, location):
        self._context = context
        self._test = test
        self._location = location

    @property
    def context(self):
        """Get the context of the location."""
        return self._context

    @property
    def test(self):
        """Get the location test."""
        return self._test

    @property
    def location(self):
        """Get the location location."""
        return self._location
