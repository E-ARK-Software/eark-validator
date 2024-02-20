#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa
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
        Information Package Package Details type
"""
from enum import Enum, unique
from importlib_resources import files
from typing import Dict, List, Optional

from pydantic import BaseModel, computed_field


@unique
class Level(str, Enum):
    """Enum covering information package validation statuses."""
    MAY = 'MAY'
    # Package has basic parse / structure problems and can't be validated
    SHOULD = 'SHOULD'
    # Package structure is OK
    MUST = 'MUST'

    @staticmethod
    def from_string(level: str) -> 'Level':
        """Convert a string to a Level."""
        for item in Level:
            if item.value == level or item.name == level:
                return item
        raise ValueError(f'No Level with value {level}')

class StructuralRequirement(BaseModel):
    """Encapsulates a structural requirement."""
    id: str
    level: Level = Level.MUST
    message: Optional[str] = None

class Requirement(BaseModel):
    """Encapsulates a requirement."""
    id: str
    name: str
    level: Level = Level.MUST
    xpath: Optional[str] = None
    cardinality: Optional[str] = None

class Specification(BaseModel):
    """Stores the vital facts and figures an IP specification."""
    title: str
    url: Optional[str] = None
    version: str
    date: str
    structural_requirements: List[StructuralRequirement] = []
    requirements: Dict[str, List[Requirement]] = {}

    @computed_field
    def id(self) -> str:
        """Return the specification id."""
        return self.url.split('/')[-1].split('.')[0].split('-')[-1]

    @computed_field
    def sections(self) -> List[str]:
        """Return the sections in the specification."""
        return list(self.requirements.keys())

    @computed_field
    def requirement_count(self) -> int:
        """Return the number of requirements."""
        return sum([len(self.requirements[sect]) for sect in self.sections])

    def section_requirements(self, section: Optional[str]=None) -> List[Requirement]:
        """Get the specification requirements, by section if offered."""
        requirements = []
        if section:
            requirements = self.requirements[section]
        else:
            for sect in self.sections:
                requirements += self.requirements[sect]
        return requirements

    def get_requirement_by_id(self, id: str) -> Optional[Requirement]:
        """Retrieve a requirement by id."""
        for sect in self.sections:
            req = self.get_requirement_by_sect(id, sect)
            if req:
                return req
        return None

    def get_requirement_by_sect(self, id: str, section: str) -> Optional[Requirement]:
        """Retrieve a requirement by id."""
        return next((req for req in self.requirements[section] if req.id == id), None)
