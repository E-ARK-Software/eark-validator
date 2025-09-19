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
from eark_validator.model.metadata import FileEntry, MetsFile, MetsRoot
from eark_validator.model.validation_report import Result
from eark_validator.model.mimetype import media_types
from eark_validator.infopacks.checksummer import Checksummer
from eark_validator.utils import get_path
from eark_validator.const import NOT_FILE, NOT_VALID_FILE
from eark_validator.specifications.specification import SpecificationVersion

NAMESPACES : str = 'namespaces'
OBJID: str = 'objid'
LABEL: str = 'label'
TYPE: str = 'type'
PROFILE: str = 'profile'
OTHERTYPE: str = 'OTHERTYPE'

START_ELE: str = 'start'
START_NS: str = 'start-ns'

class MetsFiles():
    file_paths_defined_in_mets_files: set[Path] = set()

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
                            file_entry.isValid = True
                        else:
                            file_entry.errors = errors

                        entries.append(file_entry)
        except etree.XMLSyntaxError as ex:
            raise ValueError(NOT_VALID_FILE.format(mets_file, 'XML')) from ex
        return MetsFile.model_validate({
            'root': mets_root,
            'oaispackagetype': oaispackagetype,
            'othertype': othertype,
            'contentinformationtype': contentinformationtype,
            'file_entries': entries
            })

class MetsValidator():
    """Encapsulates METS schema validation."""
    def __init__(self, mets_path: Path):
        self._validation_errors: List[Result] = []
        self._mets_path: Path = mets_path

    @property
    def validation_errors(self) -> List[Result]:
        return self._validation_errors

    @property
    def is_valid(self) -> bool:
        return len(self._validation_errors) == 0

    def validate_against_schema(self) -> bool:
        #get correct schema
        schema_path: str = IP_SCHEMA.get('csip')

        with open(schema_path, 'rb') as schema_file:
            schema_doc = etree.parse(schema_file)
            schema = etree.XMLSchema(schema_doc)

        with open(self._mets_path, 'rb') as xml_file:
            xml_doc = etree.parse(xml_file)

        is_valid = schema.validate(xml_doc)

        for error in schema.error_log:
            self._validation_errors.append(
                Result.model_validate({
                    'rule_id': 'XML',
                    'location': f"Line {error.line}, Column {error.column}",
                    'message': f"File {self._mets_path} is not valid XML. {error.message}",
                    'severity': 'Error'
                    })
            )

        return is_valid

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
    else:
        MetsFiles.file_paths_defined_in_mets_files.add(full_path)

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
    if element.tag in [ Namespaces.METS.qualify('file'), 'file']:
        tag: str = Namespaces.METS.qualify('FLocat') if hasattr(element, 'nsmap') else 'FLocat'
        flocat: Optional[etree.Element] = element.find(tag)
        if flocat is None:
            return None
        return _get_path_attrib(flocat)
    if element.tag in [Namespaces.METS.qualify('mdRef'), 'mdRef']:
        return _get_path_attrib(element)
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

    if tag == 'file':
        return 'CSIP79'
    elif tag == 'mptr':
        return 'CSIP110'

    parent = element.getparent()
    parent_tag = _get_tag_value(parent)
    match parent_tag:
        case 'dmdSec':
            return 'CSIP24'
        case 'digiprovMD':
            return 'CSIP38'
        case 'rightsMD':
            return 'CSIP51'
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')

def _get_size_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case 'dmdSec':
            return 'CSIP27'
        case 'digiprovMD':
            return 'CSIP41'
        case 'rightsMD':
            return 'CSIP54'
        case 'fileGrp':
            return 'CSIP69'
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')

def _get_checksum_algorithm_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case 'dmdSec':
            return 'CSIP30'
        case 'digiprovMD':
            return 'CSIP44'
        case 'rightsMD':
            return 'CSIP57'
        case 'fileGrp':
            return 'CSIP72'
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')

def _get_checksum_value_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case 'dmdSec':
            return 'CSIP29'
        case 'digiprovMD':
            return 'CSIP43'
        case 'rightsMD':
            return 'CSIP56'
        case 'fileGrp':
            return 'CSIP71'
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')

def _get_mimetype_requirement_id(element: etree.Element) -> str:
    element_parent: etree.Element = element.getparent()
    tag = _get_tag_value(element_parent)

    match tag:
        case 'dmdSec':
            return 'CSIP26'
        case 'digiprovMD':
            return 'CSIP40'
        case 'rightsMD':
            return 'CSIP53'
        case 'fileGrp':
            return 'CSIP68'
        case _:
            raise ValueError(f'Tag {tag} cannot be converted to a requirement ID.')

def _get_tag_value(element: etree.Element) -> str:
    index: int = element.tag.find('}')
    return element.tag if index == -1 else element.tag[index+1:]
