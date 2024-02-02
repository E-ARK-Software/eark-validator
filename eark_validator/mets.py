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
from pathlib import Path
from typing import Dict, List

from lxml import etree

from eark_validator.ipxml.schema import IP_SCHEMA
from eark_validator.ipxml.namespaces import Namespaces
from eark_validator.model.checksum import Checksum, ChecksumAlg
from eark_validator.model.metadata import FileEntry, MetsFile
from eark_validator.utils import get_path
from eark_validator.const import NOT_FILE, NOT_VALID_FILE

class MetsFiles():
    @staticmethod
    def from_file(mets_file: Path | str):
        path: Path = get_path(mets_file, True)
        if (not path.is_file()):
            raise ValueError(NOT_FILE.format(mets_file))
        ns: dict[str, str] = {}
        entries: list[FileEntry] = []
        objid = label = pkg_type = othertype = contentinformationtype = profile = oaispackagetype = ''
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
                        pkg_type = element.get('TYPE', '')
                        othertype = element.get(Namespaces.CSIP.qualify('OTHERTYPE'), '')
                        contentinformationtype = element.get(Namespaces.CSIP.qualify('CONTENTINFORMATIONTYPE'), '')
                        profile = element.get('PROFILE', '')
                    elif element.tag == Namespaces.METS.qualify('metsHdr'):
                        oaispackagetype = element.get(Namespaces.CSIP.qualify('OAISPACKAGETYPE'), '')
                    elif element.tag == Namespaces.METS.qualify('file') | element.tag == Namespaces.METS.qualify('mdRef'):
                        entries.append(_parse_file_entry(element))
        except etree.XMLSyntaxError:
            raise ValueError(NOT_VALID_FILE.format(mets_file, 'XML'))
        return MetsFile.model_validate({
            'default_ns': ns,
            'oaispackagetype': oaispackagetype,
            'objid': objid,
            'label': label,
            'type': pkg_type,
            'othertype': othertype,
            'contentinformationtype': contentinformationtype,
            'profile': profile,
            'file_entries': entries
            })

class MetsValidator():
    """Encapsulates METS schema validation."""
    def __init__(self, root: str):
        self._validation_errors: List[str] = []
        self._package_root: str = root
        self._reps_mets: Dict[str , str] = {}
        self._file_refs: List[FileEntry] = []

    @property
    def root(self) -> str:
        return self._package_root

    @property
    def validation_errors(self) -> List[str]:
        return self._validation_errors

    @property
    def representations(self) -> List[str]:
        return self._reps_mets.keys()

    @property
    def representation_mets(self) -> List[str]:
        return self._reps_mets.values()

    @property
    def file_references(self) -> List[FileEntry]:
        return self._file_refs

    def get_mets_path(self, rep_name: str) -> str:
        return self._reps_mets[rep_name]

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
            self._file_refs.append(_parse_file_entry(element))

    def _process_rep_div(self, element: etree.Element) -> None:
        rep = element.attrib['LABEL'].rsplit('/', 1)[1]
        for child in element.getchildren():
            if child.tag == Namespaces.METS.qualify('mptr'):
                self._reps_mets.update({rep:  child.attrib[Namespaces.XLINK.qualify('href')]})

def _parse_file_entry(element: etree.Element) -> FileEntry:
    """Create a FileItem from an etree element."""
    return FileEntry.model_validate({
        'path': _path_from_xml_element(element),
        'size': int(element.attrib['SIZE']),
        'checksum': _checksum_from_mets_element(element),
        'mimetype': element.attrib['MIMETYPE']
        })

def _path_from_xml_element(element: etree.Element) -> str:
    if element.tag in [Namespaces.METS.qualify('file'), 'file']:
        return element.find(Namespaces.METS.qualify('FLocat'), namespaces=element.nsmap).attrib[Namespaces.XLINK.qualify('href')] if hasattr(element, 'nsmap') else element.find('FLocat').attrib['href']
    elif element.tag in [Namespaces.METS.qualify('mdRef'), 'mdRef']:
        return element.attrib[Namespaces.XLINK.qualify('href')] if hasattr(element, 'nsmap') else element.find('FLocat').attrib['href']
    else:
        raise ValueError('Element {} is not a METS:file or METS:mdRef element.'.format(element.tag))

def _checksum_from_mets_element(element: etree.Element) -> Checksum:
    """Create a Checksum from an etree element."""
    # Get the child flocat element and grab the href attribute.
    return Checksum.model_validate({
        'algorithm': ChecksumAlg.from_string(element.attrib['CHECKSUMTYPE']),
        'value': element.attrib['CHECKSUM']},
            strict=True)

def _handle_rel_paths(rootpath: str, metspath: str) -> tuple[str, str]:
    if metspath.startswith('file:///') or os.path.isabs(metspath):
        return metspath.rsplit('/', 1)[0], metspath
    relpath = os.path.join(rootpath, metspath[9:]) if metspath.startswith('file://./') else os.path.join(rootpath, metspath)
    return relpath.rsplit('/', 1)[0], relpath
