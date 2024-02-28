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
from enum import Enum, unique
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from .checksum import Checksum

class ManifestEntry(BaseModel):
    path : Path | str
    size : int = 0
    checksums : List[Checksum] = []

class ManifestSummary(BaseModel):
    file_count: int = 0
    total_size: int = 0

@unique
class SourceType(str, Enum):
    """Enum covering information package validation statuses."""
    UNKNOWN = 'UNKNOWN'
    # Information level, possibly not best practise
    METS = 'METS'
    # Non-fatal issue that should be corrected
    PACKAGE = 'PACKAGE'

class Manifest(BaseModel):
    source: SourceType = SourceType.UNKNOWN
    root: Path
    summary: Optional[ManifestSummary] = None
    entries: List[ManifestEntry] = []

    @property
    def file_count(self) -> int:
        return len(self.entries)

    @property
    def total_size(self) -> int:
        return sum(entry.size for entry in self.entries)
