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

from typing import Annotated, Optional
from pydantic import BaseModel, Field, StringConstraints

from enum import Enum
import hashlib

class ChecksumAlg(str, Enum):
    """
    allowed enum values
    """
    MD5 = 'MD5'
    SHA1 = 'SHA-1'
    SHA256 = 'SHA-256'
    SHA384 = 'SHA-384'
    SHA512 = 'SHA-512'

    @classmethod
    def from_string(cls, value: str) -> Optional['ChecksumAlg']:
        search_value = value.upper() if hasattr(value, 'upper') else value
        for algorithm in ChecksumAlg:
            if (algorithm.value == search_value) or (algorithm.name == search_value) or (algorithm == value):
                return algorithm
        return None

    @classmethod
    def get_implementation(cls, algorithm: 'ChecksumAlg' = MD5):
        if isinstance(algorithm, str):
            algorithm = cls.from_string(algorithm)
        if algorithm == ChecksumAlg.SHA1:
            return hashlib.sha1()
        if algorithm == ChecksumAlg.SHA256:
            return hashlib.sha256()
        if algorithm == ChecksumAlg.SHA384:
            return hashlib.sha384()
        if algorithm == ChecksumAlg.SHA512:
            return hashlib.sha512()
        if algorithm == ChecksumAlg.MD5:
            return hashlib.md5()
        raise ValueError('Algorithm {} not supported.'.format(algorithm))

class Checksum(BaseModel):
    algorithm: ChecksumAlg = ChecksumAlg.SHA1
    value: Annotated[ str, StringConstraints(to_upper=True) ] = ''
