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
        Information Package Requirement Level type
"""

from enum import Enum, unique

from eark_validator.model import Severity

@unique
class Level(str, Enum):
    """Enum covering information package validation statuses."""
    MAY = 'MAY'
    # Package has basic parse / structure problems and can't be validated
    SHOULD = 'SHOULD'
    # Package structure is OK
    MUST = 'MUST'

def severity_from_level(level) -> Severity:
    """Return the correct test result severity from a Level instance."""
    if level is Level.MUST:
        return Severity.Error
    if level is Level.SHOULD:
        return Severity.Warning
    return Severity.Information
