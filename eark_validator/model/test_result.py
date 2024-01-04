#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
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
"""
E-ARK : Information Package Validation
        Information Package Validate Test Result type
"""

from eark_validator.model.severity import Severity

class TestResult:
    def __init__(self, rule_id: str=None, location: str=None, message: str=None, severity: Severity=None):  # noqa: E501
        """TestResult - a model defined in Swagger

        :param rule_id: The rule_id of this TestResult.  # noqa: E501
        :type rule_id: str
        :param location: The location of this TestResult.  # noqa: E501
        :type location: str
        :param message: The message of this TestResult.  # noqa: E501
        :type message: str
        :param severity: The severity of this TestResult.  # noqa: E501
        :type severity: Severity
        """
        self._rule_id = rule_id
        self._location = location
        self._message = message
        self._severity = severity

    @property
    def rule_id(self) -> str:
        """Gets the rule_id of this TestResult.


        :return: The rule_id of this TestResult.
        :rtype: str
        """
        return self._rule_id

    @rule_id.setter
    def rule_id(self, rule_id: str):
        """Sets the rule_id of this TestResult.


        :param rule_id: The rule_id of this TestResult.
        :type rule_id: str
        """
        self._rule_id = rule_id

    @property
    def location(self) -> str:
        """Gets the location of this TestResult.


        :return: The location of this TestResult.
        :rtype: str
        """
        return self._location

    @location.setter
    def location(self, location: str):
        """Sets the location of this TestResult.


        :param location: The location of this TestResult.
        :type location: str
        """
        self._location = location

    @property
    def message(self) -> str:
        """Gets the message of this TestResult.


        :return: The message of this TestResult.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this TestResult.


        :param message: The message of this TestResult.
        :type message: str
        """
        self._message = message

    @property
    def severity(self) -> Severity:
        """Gets the severity of this TestResult.


        :return: The severity of this TestResult.
        :rtype: Severity
        """
        return self._severity

    @severity.setter
    def severity(self, severity: Severity):
        """Sets the severity of this TestResult.


        :param severity: The severity of this TestResult.
        :type severity: Severity
        """
        self._severity = severity

    def __str__(self) -> str:
        return f'ID: {self.rule_id}, severity: {self.severity}, location: {self.location}, {self.message}'
