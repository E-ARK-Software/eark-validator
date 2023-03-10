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
from enum import Enum, unique
from lxml import etree as ET
import os

from importlib_resources import files

from ip_validation.xml import PROFILES
from ip_validation.xml.schema import METS_PROF_SCHEMA
from ip_validation.xml.namespaces import Namespaces
from ip_validation.specifications.struct_reqs import STRUCT_REQS
from ip_validation.const import NOT_FILE, NO_PATH

class Specification:
    """Stores the vital facts and figures an IP specification."""
    def __init__(self, title: str, url: str, version: str, date: str, requirements:dict[str, 'Requirement']=None):
        self._title = title
        self._url = url
        self._version = version
        self._date = date
        self._requirements = requirements if requirements else {}

    @property
    def id(self) -> str:
        """Get the id of the specification."""
        return EarkSpecifications.from_id(self.url).name

    @property
    def title(self) -> str:
        """Get the name of the specification."""
        return self._title

    @property
    def url(self) -> str:
        """Get the name of the specification."""
        return self._url

    @property
    def version(self) -> str:
        """Get the version."""
        return self._version

    @property
    def date(self) -> str:
        """Return the specification date."""
        return self._date

    @property
    def requirements(self):
        """Get the specification rules."""
        for section in self.sections:
            for requirement in self._requirements[section].values():
                yield requirement

    @property
    def requirement_count(self) -> int:
        """Return the number of requirments in the specification."""
        req_count = 0
        for sect in self.sections:
            req_count += len(self._requirements[sect])
        return req_count

    def get_requirement_by_id(self, id: str) -> 'Requirement':
        """Retrieve a requirement by id."""
        for sect in self.sections:
            req = self.get_requirement_by_sect(id, sect)
            if req:
                return req
        return None

    def get_requirement_by_sect(self, id: str, section: str) -> 'Requirement':
        """Retrieve a requirement by id."""
        sect = self._requirements[section]
        if sect:
            return sect.get(id)
        return None

    def section_requirements(self, section: str=None) -> list['Requirement']:
        """Get the specification requirements, by section if offered."""
        requirements = []
        if section:
            requirements = self._requirements[section]
        else:
            for sect in self.sections:
                requirements += self._requirements[sect].values()
        return requirements

    @property
    def section_count(self) -> int:
        """Get the specification sections."""
        return len(self._requirements)

    @property
    def sections(self) -> list[str]:
        """Get the specification sections."""
        return self._requirements.keys()

    def __str__(self) -> str:
        return 'name:' + self.title + ', version:' + \
            str(self.version) + ', date:' + str(self.date)

    @classmethod
    def _from_xml_file(cls, xml_file: str, add_struct: bool=False) -> 'Specification':
        if not os.path.exists(xml_file):
            raise FileNotFoundError(NO_PATH.format(xml_file))
        if not os.path.isfile(xml_file):
            raise ValueError(NOT_FILE.format(xml_file))
        """Create a Specification from an XML file."""
        tree = ET.parse(xml_file, parser=cls._parser())
        return  cls._from_xml(tree, add_struct=add_struct)

    @classmethod
    def _parser(cls) -> ET.XMLParser:
        """Create a parser for the specification."""
        parser = ET.XMLParser(schema=METS_PROF_SCHEMA, resolve_entities=False, no_network=True)
        return parser

    @classmethod
    def _from_xml(cls, tree: ET.ElementTree, add_struct: bool=False) -> 'Specification':
        spec = cls.from_element(tree.getroot(), add_struct=add_struct)
        return spec

    @classmethod
    def from_element(cls, spec_ele: ET.Element, add_struct: bool=False) -> 'Specification':
        """Create a Specification from an XML element."""
        version = spec_ele.get('ID')
        title = date = ''
        requirements = {}
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
        if add_struct:
            # Add the structural requirements
            struct_reqs = Specification.StructuralRequirement._get_struct_reqs()
            requirements['structure'] = struct_reqs
        # Return the Specification
        return cls(title, profile, version, date, requirements=requirements)

    @classmethod
    def _processs_requirements(cls, req_root: ET.Element) -> dict[str, 'Requirement']:
        requirements = {}
        for sect_ele in req_root:
            section = sect_ele.tag.replace(Namespaces.PROFILE.qualifier, '')
            reqs = {}
            for req_ele in sect_ele:
                requirement = cls.Requirement.from_element(req_ele)
                if not requirement.id.startswith('REF_'):
                    reqs.update({requirement.id: requirement})
            requirements[section] = reqs
        return requirements

    class Requirement():
        """Encapsulates a requirement."""
        def __init__(self, req_id: str, name: str, level: str='MUST', xpath: str=None, cardinality: str=None):
            self._id = req_id
            self._name = name
            self._level = level
            self._xpath = xpath
            self._cardinality = cardinality

        @property
        def id(self) -> str: # pylint: disable-msg=C0103
            """Return the id."""
            return self._id

        @property
        def name(self) -> str:
            """Return the name."""
            return self._name

        @property
        def level(self) -> str:
            """Return the level."""
            return self._level

        @property
        def xpath(self) -> str:
            """Return the xpath."""
            return self._xpath

        @property
        def cardinality(self) -> str:
            """Return the cardinality."""
            return self._cardinality

        def __str__(self) -> str:
            return 'id:' + self.id + ', name:' + self.name

        @classmethod
        def from_element(cls, req_ele: ET.Element) -> 'Specification.Requirement':
            """Return a Requirement instance from an XML element."""
            req_id = req_ele.get('ID')
            level = req_ele.get('LEVEL')
            name = ''
            for child in req_ele:
                if child.tag == Namespaces.METS.qualify('description'):
                    for req_child in child:
                        if req_child.tag == Namespaces.METS.qualify('head'):
                            name = req_child.text
            return cls(req_id, name, level)

    class StructuralRequirement():
        """Encapsulates a structural requirement."""
        def __init__(self, req_id: str, level: str='MUST', message: str=None):
            self._id = req_id
            self._level = level
            self._message = message

        @property
        def id(self) -> str: # pylint: disable-msg=C0103
            """Return the id."""
            return self._id

        @property
        def level(self) -> str:
            """Return the level."""
            return self._level

        @property
        def message(self) -> str:
            """Return the message."""
            return self._message

        def __str__(self) -> str:
            return 'id:' + self.id + ', level:' + str(self.level)

        @classmethod
        def from_rule_no(cls, rule_no: int) -> 'Specification.StructuralRequirement':
            """Create an StructuralRequirement from a numerical rule id and a sub_message."""
            item = STRUCT_REQS.get(rule_no)
            return cls.from_dict_item(item)

        @classmethod
        def from_dict_item(cls, item: ET.Element) -> 'Specification.StructuralRequirement':
            """Create an StructuralRequirement from dictionary item and a sub_message."""
            return cls.from_values(item.get('id'), item.get('level'),
                                   item.get('message'))

        @classmethod
        def from_values(cls, req_id: str, level: str='MUST', message:str=None) -> 'Specification.StructuralRequirement':
            """Create an StructuralRequirement from values supplied."""
            return cls(req_id, level, message)

        @staticmethod
        def _get_struct_reqs() -> list['Specification.StructuralRequirement']:
            reqs = []
            for req_num in STRUCT_REQS:
                req = STRUCT_REQS.get(req_num)
                reqs.append(Specification.StructuralRequirement(req.get('id'),
                                                                level=req.get('level'),
                                                                message=req.get('message')))
            return reqs


@unique
class EarkSpecifications(Enum):
    """Enumeration of E-ARK specifications."""
    CSIP = 'E-ARK-CSIP'
    SIP = 'E-ARK-SIP'
    DIP = 'E-ARK-DIP'

    def __init__(self, value: str):
        self._path = str(files(PROFILES).joinpath(value + '.xml'))
        self._specfication = Specification._from_xml_file(self._path)
        self._title = value

    @property
    def id(self) -> str:
        """Get the specification id."""
        return self.name

    @property
    def path(self) -> str:
        """Get the path to the specification file."""
        self._path

    @property
    def title(self) -> str:
        """Get the specification title."""
        self._title

    @property
    def specification(self) -> Specification:
        """Get the specification."""
        return self._specfication

    @property
    def profile(self) -> str:
        """Get the specification profile url."""
        return 'https://eark{}.dilcis.eu/profile/{}.xml'.format(self.name.lower(), self.value)

    @classmethod
    def from_id(cls, id: str) -> 'EarkSpecifications':
        """Get the enum from the value."""
        for spec in cls:
            if spec.id == id or spec.value == id or spec.profile == id:
                return spec
        return None
