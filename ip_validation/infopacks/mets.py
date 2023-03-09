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
"""METS Schema validation."""
import os

from lxml import etree

from ip_validation.infopacks.manifest import FileItem, Manifest
from ip_validation.xml.schema import IP_SCHEMA
from ip_validation.xml.namespaces import Namespaces

class MetsValidator():
    """Encapsulates METS schema validation."""
    def __init__(self, root: str):
        self._validation_errors = []
        self._package_root = root
        self._reps_mets = {}
        self._file_refs = []

    @property
    def root(self) -> str:
        return self._package_root

    @property
    def validation_errors(self) -> list[str]:
        return self._validation_errors

    @property
    def representations(self) -> list[str]:
        return self._reps_mets.keys()

    @property
    def representation_mets(self) -> list[str]:
        return self._reps_mets.values()

    @property
    def file_references(self) -> list[FileItem]:
        return self._file_refs

    def get_mets_path(self, rep_name: str) -> str:
        return self._reps_mets[rep_name]

    def get_manifest(self) -> Manifest:
        return Manifest.from_file_items(self._package_root, self._file_refs)

    def validate_mets(self, mets: str) -> bool:
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
            parsed_mets = etree.iterparse(mets, schema=IP_SCHEMA.get('csip'))
            for event, element in parsed_mets:
                self._process_element(element)
        except etree.XMLSyntaxError as synt_err:
            self._validation_errors.append(synt_err)
        return len(self._validation_errors) == 0

    def _process_element(self, element: etree.Element) -> None:
        # Define what to do with specific tags.
        if element.tag == Namespaces.METS.qualify('div') and \
            element.attrib['LABEL'].startswith('Representations/'):
            self._process_rep_div(element)
            return
        if element.tag == Namespaces.METS.qualify('file') or element.tag == Namespaces.METS.qualify('mdRef'):
            self._file_refs.append(FileItem.from_element(element))

    def _process_rep_div(self, element: etree.Element) -> None:
        rep = element.attrib['LABEL'].rsplit('/', 1)[1]
        for child in element.getchildren():
            if child.tag == Namespaces.METS.qualify('mptr'):
                metspath = child.attrib[Namespaces.XLINK.qualify('href')]
                self._reps_mets.update({rep: metspath})

def _handle_rel_paths(rootpath: str, metspath: str) -> tuple[str, str]:
    if metspath.startswith('file:///') or os.path.isabs(metspath):
        return metspath.rsplit('/', 1)[0], metspath
    relpath = os.path.join(rootpath, metspath[9:]) if metspath.startswith('file://./') else os.path.join(rootpath, metspath)
    return relpath.rsplit('/', 1)[0], relpath
