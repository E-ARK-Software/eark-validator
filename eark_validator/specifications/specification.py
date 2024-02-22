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
from enum import Enum, unique
from typing import Generator, List, Optional

from importlib_resources import files
from lxml import etree as ET

from eark_validator.const import NO_PATH, NOT_FILE
from eark_validator.ipxml.namespaces import Namespaces
from eark_validator.ipxml.resources import profiles
from eark_validator.ipxml.schema import METS_PROF_SCHEMA
from eark_validator.model.specifications import Requirement, Specification, StructuralRequirement
from eark_validator.specifications.struct_reqs import REQUIREMENTS
from eark_validator.specifications.struct_reqs import Level


class Specifications:

    @classmethod
    def _from_xml_file(cls, xml_file: str, add_struct: bool=False) -> Specification:
        if not os.path.exists(xml_file):
            raise FileNotFoundError(NO_PATH.format(xml_file))
        if not os.path.isfile(xml_file):
            raise ValueError(NOT_FILE.format(xml_file))
        """Create a Specification from an XML file."""
        tree = ET.parse(xml_file, parser=cls._parser())
        return  cls._from_xml(tree)

    @classmethod
    def _parser(cls) -> ET.XMLParser:
        """Create a parser for the specification."""
        parser = ET.XMLParser(schema=METS_PROF_SCHEMA, resolve_entities=False, no_network=True)
        return parser

    @classmethod
    def _from_xml(cls, tree: ET.ElementTree) -> Specification:
        spec = cls.from_element(tree.getroot())
        return spec

    @classmethod
    def from_element(cls, spec_ele: ET.Element) -> Specification:
        """Create a Specification from an XML element."""
        version = spec_ele.get('ID')
        title = date = ''
        requirements: dict[str, Requirement] = {}
        profile = ''
        # Loop through the child eles
        for child in spec_ele:
            if child.tag == Namespaces.PROFILE.qualify('title'):
                # Process the title element
                title = child.text
            elif child.tag == Namespaces.PROFILE.qualify('date'):
                # Grab the requirement text value
                date = child.text
            elif child.tag == Namespaces.PROFILE.qualify('structural_requirements'):
                requirements = cls._processs_requirements(child)
            elif child.tag in [Namespaces.PROFILE.qualify('URI'), 'URI']:
                profile = child.text
        # Add the structural requirements
        struct_reqs = StructuralRequirements.get_requirements()
        # Return the Specification
        return Specification.model_validate({
            'title': title,
            'url': profile,
            'version': version,
            'date': date,
            'requirements': requirements,
            'structural_requirements': struct_reqs
            })

    @classmethod
    def _processs_requirements(cls, req_root: ET.Element) -> dict[str, 'Requirement']:
        requirements = {}
        for sect_ele in req_root:
            section = sect_ele.tag.replace(Namespaces.PROFILE.qualifier, '')
            reqs = []
            for req_ele in sect_ele:
                requirement = Requirements.from_element(req_ele)
                if not requirement.id.startswith('REF_'):
                    reqs.append(requirement)
            requirements[section] = reqs
        return requirements

class Requirements():
    @staticmethod
    def from_element(req_ele: ET.Element) -> Requirement:
        """Return a Requirement instance from an XML element."""
        req_id = req_ele.get('ID')
        level: Level = Level.from_string(req_ele.get('REQLEVEL'))
        name = ''
        for child in req_ele:
            if child.tag == Namespaces.PROFILE.qualify('description'):
                for req_child in child:
                    if req_child.tag == Namespaces.PROFILE.qualify('head'):
                        name = req_child.text
        return Requirement.model_validate({
            'id': req_id,
            'name': name,
            'level': level
            })

class StructuralRequirements():
    @staticmethod
    def from_rule_no(rule_no: int) -> StructuralRequirement:
        """Create an StructuralRequirement from a numerical rule id and a sub_message."""
        item = REQUIREMENTS.get(rule_no)
        if not item:
            raise ValueError(f'No rule with number {rule_no}')
        return StructuralRequirements.from_dictionary(item)

    @staticmethod
    def from_dictionary(item: dict[str, str]) -> StructuralRequirement:
        """Create an StructuralRequirement from dictionary item and a sub_message."""
        return StructuralRequirement.model_validate({
                'id': item.get('id'),
                'level': item.get('level'),
                'message': item.get('message')
            })

    @staticmethod
    def get_requirements() -> list[StructuralRequirement]:
        reqs = []
        for req in REQUIREMENTS.values():
            reqs.append(StructuralRequirement.model_validate(req))
        return reqs


@unique
class EarkSpecifications(str, Enum):
    """Enumeration of E-ARK specifications."""
    CSIP = 'E-ARK-CSIP'
    SIP = 'E-ARK-SIP'
    DIP = 'E-ARK-DIP'

    def __init__(self, value: str):
        self._path = str(files(profiles).joinpath(value + '.xml'))
        self._specfication = Specifications._from_xml_file(self._path)
        self._title = value

    @property
    def id(self) -> str:
        """Get the specification id."""
        return self.name

    @property
    def path(self) -> str:
        """Get the path to the specification file."""
        return self._path

    @property
    def title(self) -> str:
        """Get the specification title."""
        return self._title

    @property
    def specification(self) -> Specification:
        """Get the specification."""
        return self._specfication

    @property
    def profile(self) -> str:
        """Get the specification profile url."""
        return 'https://eark{}.dilcis.eu/profile/{}.xml'.format(self.name.lower(), self.value)

    @classmethod
    def from_id(cls, id: str) -> Optional['EarkSpecifications']:
        """Get the enum from the value."""
        for spec in cls:
            if spec.id == id or spec.value == id or spec.profile == id:
                return spec
        return None
