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
        Information Package Structure Results type
"""
from typing import List


from eark_validator.model.struct_status import StructureStatus
from eark_validator.model.test_result import TestResult
from eark_validator.model.severity import Severity

class StructResults:
    def __init__(self, status: StructureStatus=StructureStatus.Unknown, messages: List[TestResult]=None):  # noqa: E501
        """StructResults - a model defined in Swagger

        :param status: The status of this StructResults.  # noqa: E501
        :type status: StructStatus
        :param messages: The messages of this StructResults.  # noqa: E501
        :type messages: List[TestResult]
        """
        self.status = status
        self.messages = messages

    @property
    def status(self) -> StructureStatus:
        """Gets the status of this StructResults.


        :return: The status of this StructResults.
        :rtype: StructStatus
        """
        return self._status

    @status.setter
    def status(self, status: StructureStatus):
        """Sets the status of this StructResults.


        :param status: The status of this StructResults.
        :type status: StructStatus
        """
        if status not in list(StructureStatus):
            raise ValueError('Invalid value for `status`, must be one of {0}'
                             .format(list(StructureStatus)))
        self._status = status

    @property
    def messages(self) -> List[TestResult]:
        """Gets the messages of this StructResults.


        :return: The messages of this StructResults.
        :rtype: List[TestResult]
        """
        return self._messages

    @messages.setter
    def messages(self, messages: List[TestResult]):
        """Sets the messages of this StructResults.


        :param messages: The messages of this StructResults.
        :type messages: List[TestResult]
        """
        self._messages = messages

    @property
    def errors(self) -> List[TestResult]:
        return [m for m in self.messages if m.severity == Severity.Error]

    @property
    def warnings(self) -> List[TestResult]:
        return [m for m in self.messages if m.severity == Severity.Warning]

    @property
    def infos(self) -> List[TestResult]:
        return [m for m in self.messages if m.severity == Severity.Information]
