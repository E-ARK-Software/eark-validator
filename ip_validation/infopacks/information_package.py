#!/usr/bin/env python
# coding=UTF-8
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

from .const import NO_PATH, NOT_FILE, NOT_VALID_FILE
from ip_validation.infopacks import METS_NS, CSIP_NS
from ip_validation.infopacks.manifest import Manifest

class InformationPackage:
    """Stores the vital facts and figures about a package."""
    def __init__(self, path, details, manifest=None):
        self._path = path
        self._details = details
        self._manifest = manifest if manifest else Manifest.from_directory(path)

    @property
    def path(self):
        """Get the specification of the package."""
        return self._path

    @property
    def details(self):
        """Get the package details."""
        return self._details

    @property
    def manifest(self):
        """Return the package manifest."""
        return self._manifest

class PackageDetails:

    def __init__(self, objid, label, type, othertype, contentinformationtype, profile, oaispackagetype, ns):
        self._objid = objid
        self._label = label
        self._type = type
        self._othertype = othertype
        self._contentinformationtype = contentinformationtype
        self._profile = profile
        self._oaispackagetype = oaispackagetype
        self._ns = ns

    @property
    def objid(self):
        return self._objid

    @property
    def label(self):
        return self._label

    @property
    def type(self):
        return self._type

    @property
    def othertype(self):
        return self._othertype

    @property
    def contentinformationtype(self):
        return self._contentinformationtype

    @property
    def profile(self):
        return self._profile

    @property
    def oaispackagetype(self):
        return self._oaispackagetype

    @property
    def namespaces(self):
        return self._ns

    @classmethod
    def from_mets_file(cls, mets_file):
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
                    if element.tag == _q(METS_NS, 'mets'):
                        objid = element.get('OBJID', '')
                        label = element.get('LABEL', '')
                        ptype = element.get('TYPE', '')
                        othertype = element.get(_q(CSIP_NS, 'OTHERTYPE'), '')
                        contentinformationtype = element.get(_q(CSIP_NS, 'CONTENTINFORMATIONTYPE'), '')
                        profile = element.get('PROFILE', '')
                        oaispackagetype = element.find(_q(METS_NS, 'metsHdr')).get(_q(CSIP_NS, 'OAISPACKAGETYPE'), '')
                    elif element.tag == _q(METS_NS, 'metsHdr'):
                        break
        except etree.XMLSyntaxError as synt_err:
            raise ValueError(NOT_VALID_FILE.format(mets_file, 'XML'))
        return cls(objid, label, ptype, othertype, contentinformationtype, profile, oaispackagetype, ns)

def _q(_ns, _v):
    return '{{{}}}{}'.format(_ns, _v)
