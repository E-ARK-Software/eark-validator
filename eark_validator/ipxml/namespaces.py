#!/usr/bin/env python
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
E-ARK : Information package validation
        METS/E-ARK namespaces.
"""
from enum import Enum, unique

@unique
class Namespaces(str, Enum):
    """Enumeration of the common namespace prefixes and URIs used in METS and E-ARK."""
    METS = 'http://www.loc.gov/METS/'
    CSIP = 'https://DILCIS.eu/XML/METS/CSIPExtensionMETS'
    SIP = 'https://DILCIS.eu/XML/METS/SIPExtensionMETS'
    XML = 'http://www.w3.org/XML/1998/namespace'
    XHTML = 'http://www.w3.org/1999/xhtml'
    XLINK = 'http://www.w3.org/1999/xlink'
    PROFILE = 'http://www.loc.gov/METS_Profile/v2'
    XSI = 'http://www.w3.org/2001/XMLSchema-instance'

    def __init__(self, value: str):
        self._uri = value
        self._qualifier = f'{{{value}}}'
        self._prefix = self.name.lower()

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def qualifier(self) -> str:
        return self._qualifier

    def qualify(self, value: str) -> str:
        return _qualify(self.qualifier, value)

    @classmethod
    def from_uri(cls, uri: str) -> 'Namespaces':
        for namespace in cls:
            if namespace.uri == uri:
                return namespace
        return cls.METS

    @classmethod
    def from_prefix(cls, prefix: str) -> 'Namespaces':
        """Request a namespace instance by prefix.

        Args:
            prefix (str): the prefix of the namespace to be returned.

        Returns:
            Namespaces: The namespace instance with the given prefix.
        """
        search: str = prefix.lower() if prefix else ''
        for namespace in cls:
            if namespace.prefix == search:
                return namespace
        return cls.METS

def _qualify(_ns: str, _v: str) -> str:
    return f'{_ns}{_v}'
