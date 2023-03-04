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

from ip_validation.infopacks.resources import SCHEMA
from ip_validation.infopacks.manifest import FileItem, Manifest

XLINK_NS = 'http://www.w3.org/1999/xlink'
METS_NS = 'http://www.loc.gov/METS/'
DILCIS_EXT_NS = 'https://DILCIS.eu/XML/METS/CSIPExtensionMETS'
METS_SCHEMA_LOC=str(files(SCHEMA).joinpath('mets.xsd'))
METS_SCHEMA = etree.XMLSchema(file=METS_SCHEMA_LOC)

class MetsValidator():
    """Encapsulates METS schema validation."""
    def __init__(self, root):
        self._validation_errors = []
        self._package_root = root
        self._reps_mets = {}
        self._file_refs = []

    @property
    def root(self):
        return self._package_root

    @property
    def validation_errors(self):
        return self._validation_errors

    @property
    def representations(self):
        return self._reps_mets.keys()

    @property
    def representation_mets(self):
        return self._reps_mets.values()

    @property
    def file_references(self):
        return self._file_refs

    def get_mets_path(self, rep_name):
        return self._reps_mets[rep_name]

    def get_manifest(self):
        return Manifest.from_file_items(self._package_root, self._file_refs)

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
        self._package_root, mets = _handle_rel_paths(self._package_root, mets)
        try:
            parsed_mets = etree.iterparse(mets, schema=METS_SCHEMA)
            for event, element in parsed_mets:
                self._process_element(element)
        except etree.XMLSyntaxError as synt_err:
            self._validation_errors.append(synt_err)
        return len(self._validation_errors) == 0

    def _process_element(self, element):
        # Define what to do with specific tags.
        if element.tag == _q(METS_NS, 'div') and \
            element.attrib['LABEL'].startswith('Representations/'):
            self._process_rep_div(element)
            return
        if element.tag == _q(METS_NS, 'file'):
            self._file_refs.append(FileItem.from_file_element(element))
        elif element.tag == _q(METS_NS, 'mdRef'):
            self._file_refs.append(FileItem.from_mdref_element(element))

    def _process_rep_div(self, element):
        rep = element.attrib['LABEL'].rsplit('/', 1)[1]
        for child in element.getchildren():
            if child.tag == _q(METS_NS, 'mptr'):
                metspath = child.attrib[_q(XLINK_NS, 'href')]
                self._reps_mets.update({rep: metspath})

def _handle_rel_paths(rootpath, metspath):
    if metspath.startswith('file:///') or os.path.isabs(metspath):
        return metspath.rsplit('/', 1)[0], metspath
    relpath = os.path.join(rootpath, metspath[9:]) if metspath.startswith('file://./') else os.path.join(rootpath, metspath)
    return relpath.rsplit('/', 1)[0], relpath

def _q(_ns, _v):
    return '{{{}}}{}'.format(_ns, _v)
