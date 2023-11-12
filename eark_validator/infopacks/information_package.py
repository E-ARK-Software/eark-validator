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
"""Module covering information package structure validation and navigation."""
import os
from lxml import etree

from eark_validator.const import NO_PATH, NOT_FILE, NOT_VALID_FILE
from eark_validator.xml.namespaces import Namespaces
from eark_validator.infopacks.manifest import Manifest

class PackageDetails:

    def __init__(
            self: str,
            objid: str,
            label: str,
            type: str,
            othertype: str,
            contentinformationtype: str,
            profile: str,
            oaispackagetype: str,
            ns: str):
        self._objid = objid
        self._label = label
        self._type = type
        self._othertype = othertype
        self._contentinformationtype = contentinformationtype
        self._profile = profile
        self._oaispackagetype = oaispackagetype
        self._ns = ns

    @property
    def objid(self) -> str:
        return self._objid

    @property
    def label(self) -> str:
        return self._label

    @property
    def type(self) -> str:
        return self._type

    @property
    def othertype(self) -> str:
        return self._othertype

    @property
    def contentinformationtype(self) -> str:
        return self._contentinformationtype

    @property
    def profile(self) -> str:
        return self._profile

    @property
    def oaispackagetype(self) -> str:
        return self._oaispackagetype

    @property
    def namespaces(self) -> str:
        return self._ns

    @classmethod
    def from_mets_file(cls, mets_file: str) -> 'PackageDetails':
        if (not os.path.exists(mets_file)):
            raise FileNotFoundError(NO_PATH.format(mets_file))
        if (not os.path.isfile(mets_file)):
            raise ValueError(NOT_FILE.format(mets_file))
        ns = {}
        objid = label = ptype = othertype = contentinformationtype = profile = oaispackagetype = ''
        try:
            parsed_mets = etree.iterparse(mets_file, events=['start', 'start-ns'])
            for event, element in parsed_mets:
                if event == 'start-ns':
                    prefix = element[0]
                    ns_uri = element[1]
                    ns[prefix] = ns_uri
                if event == 'start':
                    if element.tag == Namespaces.METS.qualify('mets'):
                        objid = element.get('OBJID', '')
                        label = element.get('LABEL', '')
                        ptype = element.get('TYPE', '')
                        othertype = element.get(Namespaces.CSIP.qualify('OTHERTYPE'), '')
                        contentinformationtype = element.get(Namespaces.CSIP.qualify('CONTENTINFORMATIONTYPE'), '')
                        profile = element.get('PROFILE', '')
                        oaispackagetype = element.find(Namespaces.METS.qualify('metsHdr')).get(Namespaces.CSIP.qualify('OAISPACKAGETYPE'), '')
                    elif element.tag == Namespaces.METS.qualify('metsHdr'):
                        break
        except etree.XMLSyntaxError:
            raise ValueError(NOT_VALID_FILE.format(mets_file, 'XML'))
        return cls(objid, label, ptype, othertype, contentinformationtype, profile, oaispackagetype, ns)


class InformationPackage:
    """Stores the vital facts and figures about a package."""
    def __init__(self, path: str, details: PackageDetails, manifest: Manifest=None):
        self._path = path
        self._details = details
        self._manifest = manifest if manifest else Manifest.from_directory(path)

    @property
    def path(self) -> str:
        """Get the specification of the package."""
        return self._path

    @property
    def details(self) -> PackageDetails:
        """Get the package details."""
        return self._details

    @property
    def manifest(self) -> Manifest:
        """Return the package manifest."""
        return self._manifest
