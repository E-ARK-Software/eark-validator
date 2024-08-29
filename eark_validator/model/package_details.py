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
    name: str = ''
    label: str = ''
    oaispackagetype: str = ''
    othertype: str = ''
    contentinformationtype: str = ''
    checksums: List[Checksum] = []

    # Validator to add a hyphen to the SHA checksum algorithm IDs generated by commons-ip
    @model_validator(mode='before')
    @classmethod
    def convert_checksum_ids(cls, data: Any) -> Any:
        incoming_checksums = data.get('checksums', [])
        if isinstance(incoming_checksums, list):
            # If the details are a dict type then it's a commons-ip set
            checksums : list[Checksum] = []
            # Loop through the checksums
            for checksum in incoming_checksums:
                alg_name = checksum.get('algorithm')
                if alg_name and alg_name.startswith('SHA') and '-' not in alg_name:
                    # If it's a SHA checksum alg ID without a hyphen, add one
                    alg_name = f'{alg_name[:3]}-{alg_name[3:]}'
                checksums.append(Checksum(algorithm=alg_name, value=checksum.get('value')))
            data['checksums'] = checksums
        # Return the reps for further validation.
        return data

class Representation(BaseModel):
    mets: Optional[MetsFile] = None
    name: Optional[str] = ''

class InformationPackage(BaseModel):
    mets: Optional[MetsFile] = None
    details: Optional[PackageDetails] = None
    representations: List[Representation] = []

    # Validator to convert the commons-ip representations dict to a list of representations
    @model_validator(mode='before')
    @classmethod
    def convert_representations_dict(cls, data: Any) -> Any:
        representations = data.get('representations')
        if isinstance(representations, dict):
            # If this is a dict type then it's a commons-ip type, coerce to list
            reps : list[Representation] = []
            for k, v in representations.items():
                reps.append(Representation(name=v,))
            data['representations'] = reps
        # Return the reps for further validation.
        return data
