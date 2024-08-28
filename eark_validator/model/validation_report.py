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

from pydantic import BaseModel, ConfigDict, Field

from .package_details import InformationPackage
from .specifications import Level
from .constants import (
    UNKNOWN, INFORMATION, WARNING, ERROR, WELLFORMED, NOTWELLFORMED, VALID, INVALID)

@unique
class Severity(str, Enum):
    """Enum covering information package validation statuses."""
    UNKNOWN = UNKNOWN
    # Information level, possibly not best practise
    INFORMATION = INFORMATION
    # Non-fatal issue that should be corrected
    WARNING = WARNING
    # Error level message means invalid package
    ERROR = ERROR

    @classmethod
    def from_id(cls, severity_id: str) -> Optional['Severity']:
        """Get the enum from the value."""
        for severity in cls:
            if severity_id in [ severity.name, severity.value ]:
                return severity
        return None

    @classmethod
    def from_role(cls, role: str) -> Optional['Severity']:
        """Get the enum from the value."""
        search = role.lower()
        for severity in cls:
            if severity.value.lower().startswith(search):
                return severity
        raise ValueError(f'No severity found for role: {role}')

    @classmethod
    def from_level(cls, level: Level) -> 'Severity':
        """Return the correct test result severity from a Level instance."""
        if level is Level.MUST:
            return Severity.ERROR
        if level is Level.SHOULD:
            return Severity.WARNING
        return Severity.INFORMATION

class Result(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    rule_id: Optional[str] = Field(validation_alias='ruleId')
    severity: Severity = Severity.UNKNOWN
    location: str | None
    message: str | None


@unique
class StructureStatus(str, Enum):
    """Enum for information package structure status values."""
    UNKNOWN = UNKNOWN
    # Package has basic parse / structure problems and can't be validated
    NOTWELLFORMED = NOTWELLFORMED
    # Package structure is OK
    WELLFORMED = WELLFORMED

class StructResults(BaseModel):
    status: StructureStatus = StructureStatus.UNKNOWN
    messages: List[Result] = []

    @property
    def errors(self) -> List[Result]:
        return [m for m in self.messages if m.severity == Severity.ERROR]

    @property
    def warnings(self) -> List[Result]:
        return [m for m in self.messages if m.severity == Severity.WARNING]

    @property
    def infos(self) -> List[Result]:
        return [m for m in self.messages if m.severity == Severity.INFORMATION]

@unique
class MetadataStatus(str, Enum):
    """Enum for information package metadata status values."""
    UNKNOWN = UNKNOWN
    # Package metadata is valid according to the schema/schematron rules
    VALID = VALID
    # Package metadata is invalid according to the schema/schematron rules
    INVALID = INVALID

class MetadataResults(BaseModel):
    status: MetadataStatus = MetadataStatus.UNKNOWN
    messages: List[Result] = []

class MetatdataResultSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    schema_results: MetadataResults = Field(validation_alias='schemaResults')
    model_config = ConfigDict(populate_by_name=True)
    schematron_results: MetadataResults = Field(validation_alias='schematronResults')

class ValidationReport(BaseModel):
    uid: uuid.UUID = uuid.uuid4()
    structure: Optional[StructResults] = None
    metadata: Optional[MetatdataResultSet] = None
    package: Optional[InformationPackage] = None

    @property
    def is_valid(self) -> bool:
        return self.structure.status == StructureStatus.WELLFORMED and self.metadata.schema_results.status == MetadataStatus.VALID and self.metadata.schematron_results.status == MetadataStatus.VALID
