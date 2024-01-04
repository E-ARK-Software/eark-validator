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
        Information Package Package Details type
"""
from typing import List

class PackageDetails():
    def __init__(self, name: str=None, checksums: List=None):  # noqa: E501
        self._name = name
        self._checksums = checksums if checksums is not None else []

    @property
    def name(self) -> str:
        """Gets the name of this PackageDetails.


        :return: The name of this PackageDetails.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this PackageDetails.


        :param name: The name of this PackageDetails.
        :type name: str
        """

        self._name = name

    @property
    def checksums(self) -> List:
        """Gets the checksums of this PackageDetails.


        :return: The checksums of this PackageDetails.
        :rtype: List[Checksum]
        """
        return self._checksums

    @checksums.setter
    def checksums(self, checksums: List):
        """Sets the checksums of this PackageDetails.


        :param checksums: The checksums of this PackageDetails.
        :type checksums: List[Checksum]
        """

        self._checksums = checksums
