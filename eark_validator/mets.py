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
from typing import Optional

from eark_validator.ipxml.schema import IP_SCHEMA
from eark_validator.ipxml.namespaces import Namespaces
from eark_validator.model.checksum import Checksum, ChecksumAlg
from eark_validator.model.metadata import FileEntry, InvalidFileEntry, MetsFile, MetsRoot
from eark_validator.model.validation_report import Result
from eark_validator.model.mimetype import media_types
from eark_validator.infopacks.checksummer import Checksummer
from eark_validator.utils import get_path
from eark_validator.const import NOT_FILE, NOT_VALID_FILE

NAMESPACES : str = 'namespaces'
OBJID: str = 'objid'
LABEL: str = 'label'
TYPE: str = 'type'
PROFILE: str = 'profile'
OTHERTYPE: str = 'OTHERTYPE'

START_ELE: str = 'start'
START_NS: str = 'start-ns'

class MetsFiles():
    @staticmethod
    def details_from_mets_root(namespaces: dict[str,str], root_element: etree.Element) -> MetsRoot:
        return MetsRoot.model_validate({
            NAMESPACES: namespaces,
            OBJID: root_element.get(OBJID.upper(), ''),
            LABEL: root_element.get(LABEL.upper(), ''),
            TYPE: root_element.get(TYPE.upper(), ''),
            PROFILE: root_element.get(PROFILE.upper(), '')
            })

    @staticmethod
    def from_file(mets_file: Path | str) -> MetsFile:
        path: Path = get_path(mets_file, True)
        if not path.is_file():
            raise ValueError(NOT_FILE.format(mets_file))
        ns: dict[str, str] = {}
        entries: list[FileEntry] = []
        invalid_entries: list[InvalidFileEntry] = []
        othertype = contentinformationtype = oaispackagetype = mets_root = ''
        try:
            parsed_mets = etree.iterparse(mets_file, events=[START_ELE, START_NS])
            for event, element in parsed_mets:
                if event == START_NS:
                    prefix = element[0]
                    ns_uri = element[1]
                    ns[prefix] = ns_uri
                if event == 'start':
                    if element.tag == Namespaces.METS.qualify('mets'):
                        mets_root: MetsRoot = MetsFiles.details_from_mets_root(ns, element)
                        othertype = element.get(Namespaces.CSIP.qualify(OTHERTYPE), '')
                        contentinformationtype = element.get(
                            Namespaces.CSIP.qualify('CONTENTINFORMATIONTYPE'),
                            ''
                        )
                    elif element.tag == Namespaces.METS.qualify('metsHdr'):
                        oaispackagetype = element.get(
                            Namespaces.CSIP.qualify('OAISPACKAGETYPE'), ''
                        )
                    elif element.tag in [
                            Namespaces.METS.qualify('file'),
                            Namespaces.METS.qualify('mdRef')
                        ]:
                        file_entry: FileEntry = _parse_file_entry(element)
                        errors: List[str] = _validate_file_entry(file_entry, element, os.path.dirname(mets_file))

                        if len(errors) == 0:
                            entries.append(file_entry)
                        else:
                            invalid_entries.append(InvalidFileEntry.model_validate({
                                'path': file_entry.path,
                                'size': file_entry.size,
                                'checksum': file_entry.checksum,
                                'mimetype': file_entry.mimetype,
                                'errors': errors
                                }))
        except etree.XMLSyntaxError as ex:
            raise ValueError(NOT_VALID_FILE.format(mets_file, 'XML')) from ex
        return MetsFile.model_validate({
            'root': mets_root,
            'oaispackagetype': oaispackagetype,
            'othertype': othertype,
            'contentinformationtype': contentinformationtype,
            'file_entries': entries,
            'invalid_file_entries': invalid_entries
            })

class MetsValidator():
    """Encapsulates METS schema validation."""
    def __init__(self, root: str):
        self._validation_errors: List[Result] = []
        self._package_root: str = root
        self._reps_mets: Dict[str , str] = {}
        self._file_refs: List[FileEntry] = []

    @property
    def root(self) -> str:
        return self._package_root

    @property
    def validation_errors(self) -> List[Result]:
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

    @property
    def is_valid(self) -> bool:
        return len(self._validation_errors) == 0

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
            for _, element in parsed_mets:
                self._process_element(element)
        except etree.XMLSyntaxError as synt_err:
            self._validation_errors.append(
                Result.model_validate({
                    'rule_id': 'XML-1',
                    'location': synt_err.filename + str(synt_err.lineno) + str(synt_err.offset),
                    'message': f'File {mets} is not valid XML. {synt_err.msg}',
                    'severity': 'Error'
                    })
            )
        return len(self._validation_errors) == 0

    def _process_element(self, element: etree.Element) -> None:
        # Define what to do with specific tags.
        if element.tag == Namespaces.METS.qualify('div') and \
            element.attrib['LABEL'].lower().startswith('representations/'):
            self._process_rep_div(element)
            return
        if element.tag in [ Namespaces.METS.qualify('file'), Namespaces.METS.qualify('mdRef') ]:
            self._file_refs.append(_parse_file_entry(element))

    def _process_rep_div(self, element: etree.Element) -> None:
        rep = element.attrib['LABEL'].rsplit('/', 1)[1]
        for child in element.getchildren():
            if child.tag == Namespaces.METS.qualify('mptr'):
                self._reps_mets.update({
                    rep:  child.attrib[Namespaces.XLINK.qualify('href')]
                })

def _parse_file_entry(element: etree.Element) -> FileEntry:
    """Create a FileItem from an etree element."""
    return FileEntry.model_validate({
        'path': _path_from_xml_element(element),
        'size': element.attrib.get('SIZE'),
        'checksum': _checksum_from_mets_element(element),
        'mimetype': element.attrib.get('MIMETYPE')
        })

    
def _validate_file_entry(file_entry: FileEntry, element: etree.Element, root: Path) -> list[str]:
    errors: List[str] = []

    if file_entry.path is None:
        errors.append(_get_path_requirement_id(element))
        return errors
    
    full_path: Path = Path(os.path.join(root, file_entry.path))
    if not os.path.isfile(full_path):
        errors.append(_get_path_requirement_id(element))
        return errors

    if file_entry.size is None or not file_entry.size.isdecimal():
        errors.append(_get_size_requirement_id(element))
    else:
        size = int(file_entry.size)
        if os.path.getsize(full_path) != size:
            errors.append(_get_size_requirement_id(element))

    if file_entry.checksum.algorithm is None:
        errors.append(_get_checksum_algorithm_requirement_id(element))
        errors.append(_get_checksum_value_requirement_id(element))
    elif file_entry.checksum.value is None:
        errors.append(_get_checksum_value_requirement_id(element))
    elif file_entry.checksum.value is not None:
        checksum = Checksummer.from_file(full_path, file_entry.checksum.algorithm)
        if file_entry.checksum.value != checksum.value:
            errors.append(_get_checksum_value_requirement_id(element))

    if file_entry.mimetype is None or file_entry.mimetype not in media_types:
        errors.append(_get_mimetype_requirement_id(element))

    return errors

def _path_from_xml_element(element: etree.Element) -> Optional[str]:
    loc_ele: etree.Element = element
    if element.tag in [ Namespaces.METS.qualify('file'), 'file' ]:
        tag: str = Namespaces.METS.qualify('FLocat') if hasattr(element, 'nsmap') else 'FLocat'
        loc_ele = element.find(tag)
    if element.tag in [
        Namespaces.METS.qualify('file'),
        'file', Namespaces.METS.qualify('mdRef'),
        'mdRef'
        ]:
        return  _get_path_attrib(loc_ele)
    raise ValueError(f'Element {element.tag} is not a METS:file or METS:mdRef element.')

def _get_path_attrib(element: etree.Element) -> Optional[str]:
    """Get the path attribute from an etree element."""
    attrib_name = Namespaces.XLINK.qualify('href') if hasattr(element, 'nsmap') else 'href'
    return element.attrib.get(attrib_name)

def _checksum_from_mets_element(element: etree.Element) -> Optional[Checksum]:
    """Create a Checksum from an etree element."""
    # Get the child flocat element and grab the href attribute.
    try:
        algorithm = ChecksumAlg.from_string(element.attrib.get('CHECKSUMTYPE'))
    except ValueError:
        algorithm = None

    return Checksum.model_validate({
        'algorithm': algorithm,
        'value': element.attrib.get('CHECKSUM')},
            strict=True)

def _handle_rel_paths(rootpath: str, metspath: str) -> tuple[str, str]:
    if metspath.startswith('file:///') or os.path.isabs(metspath):
        return metspath.rsplit('/', 1)[0], metspath
    if metspath.startswith('file://./'):
        relpath = os.path.join(rootpath, metspath[9:])
    else:
        relpath = os.path.join(rootpath, metspath)
    return relpath.rsplit('/', 1)[0], relpath
       
def _get_path_requirement_id(element: etree.Element) -> str:
    tag = _get_tag_value(element)

    if tag == "FLocat": 
        return "CSIP79"
    elif tag == "mptr": 
        return "CSIP110"
    
    parent = element.getparent()
    parent_tag = _get_tag_value(parent)
    match parent_tag:
        case "dmdSec":
            return "CSIP24"
        case "digiprovMD": 
            return "CSIP38"
        case "rightsMD": 
            return "CSIP51"
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')
        
def _get_size_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case "dmdSec":
            return "CSIP27"
        case "digiprovMD":
            return "CSIP41"
        case "rightsMD":
            return "CSIP54"
        case "fileGrp":
            return "CSIP69"
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')
        
def _get_checksum_algorithm_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case "dmdSec":
            return "CSIP30"
        case "digiprovMD":
            return "CSIP44"
        case "rightsMD":
            return "CSIP57"
        case "fileGrp":
            return "CSIP72"
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')
        
def _get_checksum_value_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case "dmdSec":
            return "CSIP29"
        case "digiprovMD":
            return "CSIP43"
        case "rightsMD":
            return "CSIP56"
        case "fileGrp":
            return "CSIP71"
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')
        
def _get_mimetype_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case "dmdSec":
            return "CSIP26"
        case "digiprovMD":
            return "CSIP40"
        case "rightsMD":
            return "CSIP53"
        case "fileGrp":
            return "CSIP68"
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')
        
def _get_tag_value(element: etree.Element) -> str:
    index: int = element.tag.find('}')
    return element.tag if index == -1 else element.tag[index+1:]
