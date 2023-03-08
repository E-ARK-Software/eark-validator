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


from .resources.xml import schema as SCHEMA

METS_NS = 'http://www.loc.gov/METS/'
CSIP_NS = 'https://DILCIS.eu/XML/METS/CSIPExtensionMETS'
SIP_NS = 'https://DILCIS.eu/XML/METS/SIPExtensionMETS'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
XHTML_NS = 'http://www.w3.org/1999/xhtml'
XLINK_NS = 'http://www.w3.org/1999/xlink'
PROFILE_NS = 'http://www.loc.gov/METS_Profile/v2',
XSI_NS = 'http://www.w3.org/2001/XMLSchema-instance'

NS_BY_PREFIX = {
    None: METS_NS,
    'csip': CSIP_NS,
    'sip': SIP_NS,
    'xml': XML_NS,
    'xhtml': XHTML_NS,
    'xlink': XLINK_NS,
    'mets': METS_NS,
    'profile': PROFILE_NS,
    'xsi': XSI_NS
}

PREFIX_BY_URI = {}

for prefix, uri in NS_BY_PREFIX.items():
    PREFIX_BY_URI[uri] = prefix

LOCAL_SCHEMA = {
    CSIP_NS: 'DILCISExtensionMETS.xsd',
    SIP_NS: 'DILCISExtensionSIPMETS.xsd',
    XML_NS: 'xml.xsd',
    XHTML_NS: 'xhtml1-strict.xsd',
    XLINK_NS: 'xlink.xsd',
    METS_NS: 'mets.xsd',
    PROFILE_NS: 'mets-profile.v2-0.xsd'
}

IP_SCHEMA = {
    'csip': etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.csip.local.v2-0.xsd'))),
    'sip': etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.sip.local.v2-0.xsd')))
}

def get_prefix(uri):
    """Return the prefix for a given namespace URI."""
    return PREFIX_BY_URI.get(uri, PREFIX_BY_URI[METS_NS])

def  get_uri(prefix):
    """Return the namespace URI for a given prefix."""
    return NS_BY_PREFIX.get(prefix, METS_NS)

def get_local_schema(uri):
    """Return the local schema file name for a given namespace URI."""
    return str(files(SCHEMA).joinpath(LOCAL_SCHEMA.get(uri, 'mets.xsd')))
