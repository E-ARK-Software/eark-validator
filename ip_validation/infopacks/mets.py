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
"""METS Schema validation."""
import fnmatch
import os

from lxml import etree

from importlib_resources import files

import ip_validation.infopacks.resources.schemas as SCHEMA

XLINK_NS = 'http://www.w3.org/1999/xlink'
METS_NS = 'http://www.loc.gov/METS/'
DILCIS_EXT_NS = 'https://DILCIS.eu/XML/METS/CSIPExtensionMETS'

class MetsValidator():
    """Encapsulates METS schema validation."""
    def __init__(self, root):
        self.validation_errors = []
        self.total_files = 0
        self.schema_mets = etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.xsd')))
        self.rootpath = root
        self.subsequent_mets = []

    def validate_mets(self, mets):
        '''
        Validates a Mets file. The Mets file is parsed with etree.iterparse(),
        which allows event-driven parsing of large files. On certain events/conditions
        actions are taken, like file validation or adding Mets files found inside
        representations to a list so that they will be evaluated later on.

        @param mets:    Path leading to a Mets file that will be evaluated.
        @return:        Boolean validation result.
        '''
        # Handle relative package paths for representation METS files.
        self.rootpath, mets = _handle_rel_paths(self.rootpath, mets)
        try:
            parsed_mets = etree.iterparse(mets, events=('start', 'end'), schema=self.schema_mets)
            for event, element in parsed_mets:
                self._process_element(event, element)
        except etree.XMLSyntaxError as synt_err:
            self.validation_errors.append(synt_err)

        if self.total_files != 0:
            self.validation_errors.append('File count yielded %d instead of 0.' % self.total_files)

        return len(self.validation_errors) == 0

    def _process_element(self, event, element):
        # Define what to do with specific tags.
        if event != 'end':
            return
        if element.tag == _q(METS_NS, 'file'):
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
        elif element.tag == _q(METS_NS, 'div') and \
            element.attrib['LABEL'].startswith('representations/'):
            self._process_rep_div(element)


    def _process_rep_div(self, element):
        if fnmatch.fnmatch(element.attrib['LABEL'].rsplit('/', 1)[1], '*_mig-*'):
            # representation mets files
            rep = element.attrib['LABEL'].rsplit('/', 1)[1]
            for child in element.getchildren():
                if child.tag == _q(METS_NS, 'mptr'):
                    metspath = child.attrib[_q(XLINK_NS, 'href')]
                    sub_mets = rep, metspath
                    self.subsequent_mets.append(sub_mets)
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]

def _handle_rel_paths(rootpath, metspath):
    if metspath.startswith('file://./'):
        relpath = os.path.join(rootpath, metspath[9:])
        # change self.rootpath to match any relative path found in the
        # current (subsequent) mets
        return relpath.rsplit('/', 1)[0], relpath
    return metspath.rsplit('/', 1)[0], metspath


def _q(_ns, _v):
    return '{{{}}}{}'.format(_ns, _v)
