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
import logging

import lxml.etree
from lxml.isoschematron import Schematron

from importlib_resources import files

import ip_validation.resources.schematron

class ValidationRules():
    def __init__(self, name, rules_path=None):
        self.name = name
        if not rules_path:
            rules_path = 'mets_{}_rules.xml'.format(name)
        self.rules_path = str(files(ip_validation.resources.schematron).joinpath(rules_path))
        logging.debug("path: %s", self.rules_path)
        self.ruleset = Schematron(file=self.rules_path, store_schematron=True, store_report=True)

    def get_rules(self):
        return self.ruleset.schematron

    def validate(self, to_validate):
        xml_file = lxml.etree.parse(to_validate)
        return self.ruleset.validate(xml_file)

    def get_report(self):
        return self.ruleset.validation_report

class ValidationProfile():
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
        self.results['root'] = self.rulesets['root'].validate(to_validate)
        self.results['hdr'] = self.rulesets['hdr'].validate(to_validate)
        self.results['amd'] = self.rulesets['amd'].validate(to_validate)
        self.results['dmd'] = self.rulesets['dmd'].validate(to_validate)
        self.results['file'] = self.rulesets['file'].validate(to_validate)
        self.results['structmap'] = self.rulesets['structmap'].validate(to_validate)

    def get_results(self):
        return self.results

    def get_result(self, name):
        return self.results.get(name)

class TestResult():
    def __init__(self, rule_id, context, test, location, message):
        self.rule_id = rule_id
        self.context = context
        self.test = test
        self.location = location
        self.message = message

    @classmethod
    def from_element(cls, rule, failed_assert):
        rule_id = rule.get('id')
        context = rule.get('context')
        test = failed_assert.get('test')
        location = failed_assert.get('location')
        message = failed_assert.find('{http://purl.oclc.org/dsdl/svrl}text').text
        return cls(rule_id, context, test, location, message)
