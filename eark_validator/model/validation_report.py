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
        Information Package Validation Report type
"""

from enum import Enum, unique
from typing import List, Optional
import uuid

from pydantic import BaseModel

@unique
class Level(str, Enum):
    """Enum covering information package validation statuses."""
    MAY = 'MAY'
    # Package has basic parse / structure problems and can't be validated
    SHOULD = 'SHOULD'
    # Package structure is OK
    MUST = 'MUST'

@unique
class Severity(str, Enum):
    """Enum covering information package validation statuses."""
    Unknown = 'Unknown'
    # Information level, possibly not best practise
    Information = 'Information'
    # Non-fatal issue that should be corrected
    Warning = 'Warning'
    # Error level message means invalid package
    Error = 'Error'

    @classmethod
    def from_id(cls, id: str) -> Optional['Severity']:
        """Get the enum from the value."""
        for severity in cls:
            if severity.name == id or severity.value == id:
                return severity
        return None

    @classmethod
    def from_level(cls, level: Level) -> 'Severity':
        """Return the correct test result severity from a Level instance."""
        if level is Level.MUST:
            return Severity.Error
        if level is Level.SHOULD:
            return Severity.Warning
        return Severity.Information

class TestResult(BaseModel):
    rule_id: str | None
    severity: Severity | None
    location: str | None
    message: str | None

@unique
class StructureStatus(str, Enum):
    """Enum covering information package validation statuses."""
    Unknown = 'Unknown'
    # Package has basic parse / structure problems and can't be validated
    NotWellFormed = 'Not Well Formed'
    # Package structure is OK
    WellFormed = 'Well Formed'

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

class ValidationReport(BaseModel):
    uid: uuid.UUID = uuid.uuid4()
    structure: StructResults | None
