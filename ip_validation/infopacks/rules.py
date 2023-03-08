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
import os

from lxml import etree as ET

from ip_validation.xml.schematron import SchematronRuleset, SVRL_NS
from ip_validation.infopacks.specification import EarkSpecifications, Specification
from ip_validation.const import NO_PATH, NOT_FILE

class ValidationProfile():
    """ A complete set of Schematron rule sets that comprise a complete validation profile."""
    def __init__(self, specification):
        self._rulesets = {}
        self._specification = specification
        self.is_valid = False
        self.is_wellformed = False
        self.results = {}
        self.messages = []
        for section in specification.sections:
            self.rulesets[section] = SchematronRuleset(specification.id, section)

    @property
    def specification(self):
        """Get the specification."""
        return self._specification

    @property
    def rulesets(self):
        """ Get the Schematron rulesets."""
        return self._rulesets

    def validate(self, to_validate):
        """Validates a file against each loaded ruleset."""
        if not os.path.exists(to_validate):
            raise FileNotFoundError(NO_PATH.format(to_validate))
        if not os.path.isfile(to_validate):
            raise ValueError(NOT_FILE.format(to_validate))
        is_valid = True
        self.is_wellformed = True
        self.results = {}
        self.messages = []
        for section in self.rulesets.keys():
            try:
                self.rulesets[section].validate(to_validate)
            except ET.XMLSyntaxError as parse_err:
                self.is_wellformed = False
                self.is_valid = False
                self.messages.append('File {} is not valid XML. {}'.format(to_validate, parse_err.msg))
                return
            self.results[section] = TestReport.from_ruleset(self.rulesets[section].ruleset.validation_report)
            if not self.results[section].is_valid:
                is_valid = False
        self.is_valid = is_valid

    def get_results(self):
        """Return the full set of results."""
        return self.results

    def get_result(self, name):
        """Return only the results for element name."""
        return self.results.get(name)

    @classmethod
    def from_specification(cls, specification):
        """Create a validation profile from a specification."""
        if isinstance(specification, str):
            specification = EarkSpecifications.from_id(specification)
        if isinstance(specification, EarkSpecifications):
            specification = specification.specification
        if not isinstance(specification, Specification):
            raise ValueError('Specification must be a Specification instance or valid specification ID.')
        return cls(specification)

@unique
class Severity(Enum):
    """Enum covering information package validation statuses."""
    UNKNOWN = "Unknown"
    # Information level, possibly not best practise
    INFO = "Information"
    # Non-fatal issue that should be corrected
    WARN = "Warning"
    # Error level message means invalid package
    ERROR = "Error"

    @classmethod
    def from_id(cls, id):
        """Get the enum from the value."""
        for severity in cls:
            if severity.name == id or severity.value == id:
                return severity
        return None

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
        if not isinstance(value, Severity):
            value = Severity.from_id(value)
        if value not in list(Severity):
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

    def __str__(self):
        return str(self.rule_id) + " " + str(self.severity) + " " + str(self.location)

    def to_json(self):
        """Output the error message in JSON form."""
        return {"rule_id" : self.rule_id, "severity" : str(self.severity.name),
                "test" : self.location.test, "location" : self.location.location,
                "message" : self.message}

    @classmethod
    def from_element(cls, rule, failed_assert):
        """Create a Test result from an element."""
        context = rule.get('context')
        rule_id = failed_assert.get('id')
        test = failed_assert.get('test')
        severity = Severity.from_id(failed_assert.get('role', Severity.UNKNOWN.name))
        location = failed_assert.get('location')
        message = failed_assert.find(SVRL_NS + 'text').text
        schmtrn_loc = SchematronLocation(context, test, location)
        return cls(rule_id, schmtrn_loc, message, severity)


class TestReport():
    """A report made up of validation results."""
    def __init__(self, is_valid, failures, warnings, infos):
        self._is_valid = is_valid
        self._failures = failures
        self._warnings = warnings
        self._infos = infos

    @property
    def is_valid(self):
        """Get the is_valid result."""
        return self._is_valid

    @property
    def failures(self):
        """Get the failures."""
        return self._failures

    @property
    def warnings(self):
        """Get the warnings."""
        return self._warnings

    @property
    def infos(self):
        """Get the warnings."""
        return self._infos

    @classmethod
    def from_ruleset(cls, ruleset):
        """Get the report from the last validation."""
        xml_report = ET.XML(bytes(ruleset))
        failures = []
        warnings = []
        infos = []
        is_valid = True
        rule = None
        for ele in xml_report.iter():
            if ele.tag == SVRL_NS + 'fired-rule':
                rule = ele
            elif (ele.tag == SVRL_NS + 'failed-assert') or (ele.tag == SVRL_NS + 'successful-report'):
                if ele.get('role') == 'INFO':
                    infos.append(TestResult.from_element(rule, ele))
                elif ele.get('role') == 'WARN':
                    warnings.append(TestResult.from_element(rule, ele))
                else:
                    is_valid = False
                    failures.append(TestResult.from_element(rule, ele))
        return TestReport(is_valid, failures, warnings, infos)


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

    def __str__(self):
        return str(self.context) + " " + str(self.test) + " " + str(self.location)
