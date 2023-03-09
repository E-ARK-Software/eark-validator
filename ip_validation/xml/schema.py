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
"""
E-ARK : Information package validation
        Information Package modules
"""
from lxml import etree
from importlib_resources import files

from .resources import schema as SCHEMA
from .namespaces import Namespaces
IP_SCHEMA = {
    'csip': etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.csip.local.v2-0.xsd'))),
    'sip': etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.sip.local.v2-0.xsd')))
}

LOCAL_SCHEMA = {
    Namespaces.CSIP: 'DILCISExtensionMETS.xsd',
    Namespaces.SIP: 'DILCISExtensionSIPMETS.xsd',
    Namespaces.XML: 'xml.xsd',
    Namespaces.XHTML: 'xhtml1-strict.xsd',
    Namespaces.XLINK: 'xlink.xsd',
    Namespaces.METS: 'mets.xsd',
    Namespaces.PROFILE: 'mets-profile.v2-0.xsd'
}

def get_local_schema(uri: str) -> str:
    """Return the local schema file name for a given namespace URI."""
    return str(files(SCHEMA).joinpath(LOCAL_SCHEMA.get(uri, 'mets.xsd')))

METS_PROF_SCHEMA = etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.profile.local.v2-0.xsd')))
