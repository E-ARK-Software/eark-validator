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

from pydantic import BaseModel

from eark_validator.model.struct_status import StructureStatus
from eark_validator.model.test_result import TestResult
from eark_validator.model.severity import Severity

class StructResults(BaseModel):
    status: StructureStatus
    messages: List[TestResult]

    @property
    def errors(self) -> List[TestResult]:
        return [m for m in self.messages if m.severity == Severity.Error]

    @property
    def warnings(self) -> List[TestResult]:
        return [m for m in self.messages if m.severity == Severity.Warning]

    @property
    def infos(self) -> List[TestResult]:
        return [m for m in self.messages if m.severity == Severity.Information]
