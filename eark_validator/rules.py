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
from typing import Dict, List

from lxml import etree as ET

from eark_validator.ipxml.schematron import SchematronRuleset, SVRL_NS, get_schematron_path
from eark_validator.model.validation_report import Location, Result
from eark_validator.specifications.specification import EarkSpecification, Specification, SpecificationType, SpecificationVersion
from eark_validator.const import NO_PATH, NOT_FILE
from eark_validator.model import Severity

class ValidationProfile():
    """ A complete set of Schematron rule sets that comprise a complete validation profile."""
    def __init__(self, type: SpecificationType, version: SpecificationVersion):
        specification: Specification = EarkSpecification(type, version).specification

        self._rulesets: Dict[str, SchematronRuleset] = {}
        self._specification: Specification = specification
        self.is_valid: bool = False
        self.is_wellformed: bool = False
        self.results: Dict[str, List[Result]] = {}
        self.messages: List[str] = []
        for section in specification.sections:
            self.rulesets[section] = SchematronRuleset(get_schematron_path(version, specification.id, section))

    @property
    def specification(self) -> Specification:
        """Get the specification."""
        return self._specification

    @property
    def rulesets(self) -> dict[str, SchematronRuleset]:
        """ Get the Schematron rulesets."""
        return self._rulesets

    def validate(self, to_validate: str) -> None:
        """Validates a file against each loaded ruleset."""
        if not os.path.exists(to_validate):
            raise FileNotFoundError(NO_PATH.format(to_validate))
        if not os.path.isfile(to_validate):
            raise ValueError(NOT_FILE.format(to_validate))
        self.is_wellformed = True
        self.is_valid = True
        self.results = {}
        self.messages = []
        for section, validator in self.rulesets.items():
            try:
                self.results[section] = TestResults.from_validation_report(
                    validator.validate(to_validate)
                    )
                if self._contains_errors(section):
                    self.is_valid = False
            except ET.XMLSyntaxError as parse_err:
                self.is_wellformed = False
                self.is_valid = False
                self.messages.append(f'File {to_validate} is not valid XML. {parse_err.msg}')
                return

    def _contains_errors(self, section: str) -> bool:
        return len(list(filter(lambda a: a.severity == Severity.ERROR, self.results[section]))) > 0

    def get_results(self) -> dict[str,  List[Result]]:
        """Return the full set of results."""
        return self.results

    def get_all_results(self) -> List[Result]:
        """Return the full set of results."""
        results_list: List[Result] = []
        for _, results in self.results.items():
            results_list.extend(results)
        return results_list

    def get_result(self, name: str) ->  List[Result]:
        """Return only the results for element name."""
        return self.results.get(name)

class TestResults():
    @staticmethod
    def from_element(rule: ET.Element, failed_assert: ET.Element) -> Result:
        """Create a Test result from an element."""
        context = rule.get('context')
        rule_id = failed_assert.get('id')
        if isinstance(rule_id, str):
            rule_id = rule_id.split('_')[0]

        test = failed_assert.get('test')
        severity = Severity.from_role(failed_assert.get('role', Severity.ERROR))
        location = failed_assert.get('location')
        message = failed_assert.find(SVRL_NS + 'text').text
        location = Location.model_validate({
            'context':context,
            'test':test,
            'description': location
        })
        return Result.model_validate({
            'rule_id': rule_id, 'location':location, 'message':message, 'severity':severity
        })

    @staticmethod
    def from_validation_report(ruleset: ET.Element) -> List[Result]:
        """Get the report from the last validation."""
        xml_report = ET.XML(bytes(ruleset))
        rule = None
        results: List[Result] = []
        for ele in xml_report.iter():
            if ele.tag == SVRL_NS + 'fired-rule':
                rule = ele
            elif ele.tag in [ SVRL_NS + 'failed-assert', SVRL_NS + 'successful-report' ]:
                results.append(TestResults.from_element(rule, ele))
        return results
