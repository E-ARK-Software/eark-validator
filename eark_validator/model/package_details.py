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
from typing import Any, List, Optional

from pydantic import BaseModel, ValidationInfo, model_validator

from .checksum import Checksum
from .metadata import MetsFile


class PackageDetails(BaseModel):
    label: str = ''
    oaispackagetype: str = ''
    othertype: str = ''
    contentinformationtype: str = ''
    checksums: List[Checksum] = []

class Representation(BaseModel):
    mets: Optional[MetsFile] = None
    name: Optional[str] = ''

class InformationPackage(BaseModel):
    name: str = ''
    mets: Optional[MetsFile] = None
    package: Optional[PackageDetails] = None
    representations: List[Representation] = []

    @model_validator(mode='before')
    @classmethod
    def convert_dict(cls, data: Any) -> list[Representation]:
        representations = data.get('representations')
        if isinstance(representations, dict):
            # If this is a dict type then it's a commons-ip type, coerce to list
            reps : list[Representation] = []
            for k, v in representations.items():
                reps.append(Representation(name=v,))
            data['representations'] = reps
        # Return the reps for further validation.
        return data
