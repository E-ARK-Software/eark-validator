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
from pathlib import Path
from typing import Annotated, List, Optional

from pydantic import BaseModel, StringConstraints

from .checksum import Checksum

class FileEntry(BaseModel):
    path : Path | str
    size : int = 0
    checksum : Checksum
    mimetype : Annotated[ str, StringConstraints(to_lower=True) ] = 'application/octet-stream'

class MetsFile(BaseModel):
    default_ns: str
    oaispackagetype: str
    objid: str
    label: str
    type: str
    othertype: str
    contentinformationtype: str
    profile: str
    file_entries: List[FileEntry] = []
