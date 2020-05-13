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
import io
import json
import os
import re

from importlib_resources import files

from lxml import isoschematron
from lxml import etree

import ip_validation.resources

class CSIPValidation(object):

    def __init__(self, rules_path=None):
        if not rules_path:
            self.rules_path = files(ip_validation.resources).joinpath('validation_rules.xml')
        else:
            self.rules_path = rules_path
        xml_rules = self._read_rules_from_location(rules_path)
        self.rules_lines = xml_rules.split('\n')
        self.validation_report = []
        self.validation_profile = json.loads(validation_profile)
        self.valid = True

    @staticmethod
    def _get_rule(lines, rule_id):
        rules_ids = [rule_id]
        n_header_lines = 5
        rule = lines[:n_header_lines]  # add schema and namespaces
        rule_found = False
        # select all patterns with matching id
        for line in lines[n_header_lines:]:
            if not rule_found:
                # look for beginning of pattern/rule
                match = re.search('pattern id="CSIP(.+?)"', line)
                if match:
                    current_id = int(match.group(1))
                    if current_id in rules_ids:
                        # select pattern
                        rule.append(line)
                        rule_found = True
                    # else ignore pattern
                # else is not the beginning of a pattern
            elif '</pattern>' in line:
                # pattern/rule is over
                rule.append(line)
                rule_found = False
            else:
                rule.append(line)
        rule.append('</schema>\n')
        res = '\n'.join(rule)
        return res

    def _process_validation(self, xml_file, rule_id):
        # Parse rules
        single_rule = io.StringIO(CSIPValidation._get_rule(self.rules_lines, rule_id))
        parsed_single_rule = etree.parse(single_rule)
        schematron = isoschematron.Schematron(parsed_single_rule, store_report=True)

        # Parse XML to validate
        parsed_xml_file = etree.parse(xml_file)
        validation_response = schematron.validate(parsed_xml_file)
        report = schematron.validation_report
        return validation_response, report

    def validate(self, ip_path):
        for validation_block_name, validation_rules in self.validation_profile.items():
            validation_block = {validation_block_name: []}
            for rule_id in validation_rules:
                validation_result, report = self._process_validation(ip_path + '/METS.xml', rule_id=rule_id)
                validation_block[validation_block_name].append(
                    {"rule": "csip%d" % rule_id, "result": validation_result, "report": report}
                )
                # set global validation to 'invalid' if one of the rules is violated
                if not validation_result:
                    self.valid = False
            self.validation_report.append(validation_block)
        return self.validation_report

    def get_validation_profile(self):
        return self.validation_profile

    def get_rules_file_path(self):
        return self.rules_path

    def get_log_lines(self):
        log_lines = []
        for validation_blocks in self.validation_report:
            for validation_block_name, validation_results in validation_blocks.items():
                for validation_result in validation_results:
                    if validation_result['result']:
                        log_lines.append({"type": "INFO", "message": "%s - %s - validated successfully" % (
                        validation_block_name, validation_result['rule'])})
                    else:
                        nsmap = {'svrl': 'http://purl.oclc.org/dsdl/svrl'}
                        xml_report = validation_result['report']
                        res = xml_report.find('svrl:failed-assert', namespaces=nsmap)
                        log_lines.append({"type": "ERROR", "message": "%s - %s - Test: %s" % (
                        validation_block_name, validation_result['rule'], res.attrib['test'])})
                        log_lines.append({"type": "ERROR", "message": "%s - %s - Location: %s" % (
                        validation_block_name, validation_result['rule'], res.attrib['location'])})

        return log_lines

    @staticmethod
    def _read_rules_from_location(location):
        if not location:
            return files(eatb.resources).joinpath('validation_rules.xml').read_text()
        with open(location) as fp:
            return fp.read()
