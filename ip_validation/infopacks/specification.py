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
"""Module covering information package structure validation and navigation."""
import lxml.etree as ET

from importlib_resources import files

import ip_validation.cli.resources as RES
from ip_validation.infopacks.struct_reqs import STRUCT_REQS

METS_PROF_SCHEMA = ET.XMLSchema(file=str(files(RES).joinpath('mets.profile.v2-0.xsd')))
METS_PROF = str(files(RES).joinpath('E-ARK-CSIP.xml'))
METS_NS = '{http://www.loc.gov/METS_Profile/v2}'

class Specification:
    """Stores the vital facts and figures an IP specification."""
    def __init__(self, name, version, date, requirements=None):
        self._name = name
        self._version = version
        self._date = date
        self._requirements = requirements if requirements else {}

    @property
    def name(self):
        """Get the name of the specification."""
        return self._name

    @property
    def version(self):
        """Get the version."""
        return self._version

    @property
    def date(self):
        """Return the specification date."""
        return self._date

    @property
    def requirements(self):
        """Get the specification rules."""
        for section in self.sections:
            for requirement in self._requirements[section]:
                yield requirement

    @property
    def requirement_count(self):
        """Return the number of requirments in the specification."""
        req_count = 0
        for sect in self.sections:
            req_count += len(self._requirements[sect])
        return req_count

    def section_requirements(self, section=None):
        """Get the specification requirements, by section if offered."""
        requirements = []
        if section:
            requirements = self._requirements[section]
        else:
            for sect in self.sections:
                requirements += self._requirements[sect]
        return requirements

    @property
    def sections(self):
        """Get the specification rules."""
        return self._requirements.keys()

    def __str__(self):
        return "name:" + self.name + ", version:" + \
            str(self.version) + ", date:" + str(self.date)

    @classmethod
    def from_xml_string(cls, xml, schema=METS_PROF_SCHEMA):
        """Create a Specification from an XML string."""
        tree = ET.fromstring(xml)
        return cls._from_xml(tree, schema)

    @classmethod
    def from_xml_file(cls, xml_file=METS_PROF, schema=METS_PROF_SCHEMA):
        """Create a Specification from an XML file."""
        tree = ET.parse(xml_file)
        return  cls._from_xml(tree, schema)

    @classmethod
    def _from_xml(cls, tree, schema,):
        spec = cls.from_element(tree.getroot(), schema)
        return spec

    @classmethod
    def from_element(cls, spec_ele, schema=METS_PROF_SCHEMA):
        """Create a Specification from an XML element."""
        # is_valid = schema.assertValid(spec_ele)
        # if not is_valid:
        #     raise ValueError('Specification invalid')
        # Grab the testable att
        version = spec_ele.get('ID')
        name = date = ''
        requirements = {}
        # Loop through the child eles
        for child in spec_ele:
            if child.tag == '{}title'.format(METS_NS):
                # Process the title element
                name = child.text
            elif child.tag == '{}date'.format(METS_NS):
                # Grab the requirement text value
                date = child.text
            elif child.tag == '{}structural_requirements'.format(METS_NS):
                for sect_ele in child:
                    section = sect_ele.get('ID')
                    reqs = []
                    for req_ele in sect_ele:
                        requirement = cls.Requirement.from_element(req_ele)
                        if not requirement.id.startswith('REF_'):
                            reqs.append(cls.Requirement.from_element(req_ele))
                    requirements[section] = reqs
        # Add the structural requirements
        struct_reqs = Specification.StructuralRequirement._get_struct_reqs()
        requirements['structure'] = struct_reqs
        # Return the TestCase instance
        return cls(name, version, date, requirements=requirements)

    class Requirement():
        """Encapsulates a requirement."""
        def __init__(self, req_id, name, level="MUST", xpath=None, cardinality=None):
            self._id = req_id
            self._name = name
            self._level = level
            self._xpath = xpath
            self._cardinality = cardinality

        @property
        def id(self): # pylint: disable-msg=C0103
            """Return the id."""
            return self._id

        @property
        def name(self):
            """Return the name."""
            return self._name

        @property
        def level(self):
            """Return the level."""
            return self._level

        @property
        def xpath(self):
            """Return the xpath."""
            return self._xpath

        @property
        def cardinality(self):
            """Return the cardinality."""
            return self._cardinality

        def __str__(self):
            return "id:" + self.id + ", name:" + self.name

        @classmethod
        def from_element(cls, req_ele):
            """Return a Requirement instance from an XML element."""
            req_id = req_ele.get('ID')
            level = req_ele.get('LEVEL')
            name = ''
            for child in req_ele:
                if child.tag == '{http://www.loc.gov/METS_Profile/v2}description':
                    for req_child in child:
                        if req_child.tag == '{http://www.loc.gov/METS_Profile/v2}head':
                            name = req_child.text
            return cls(req_id, name, level)

    class StructuralRequirement():
        """Encapsulates a structural requirement."""
        def __init__(self, req_id, level="MUST", message=None):
            self._id = req_id
            self._level = level
            self._message = message

        @property
        def id(self): # pylint: disable-msg=C0103
            """Return the id."""
            return self._id

        @property
        def level(self):
            """Return the level."""
            return self._level

        @property
        def message(self):
            """Return the message."""
            return self._message

        def __str__(self):
            return "id:" + self.id + ", level:" + str(self.level)

        @classmethod
        def from_rule_no(cls, rule_no):
            """Create an StructuralRequirement from a numerical rule id and a sub_message."""
            item = STRUCT_REQS.get(rule_no)
            return cls.from_dict_item(item)

        @classmethod
        def from_dict_item(cls, item):
            """Create an StructuralRequirement from dictionary item and a sub_message."""
            return cls.from_values(item.get('id'), item.get('level'),
                                   item.get('message'))

        @classmethod
        def from_values(cls, req_id, level="MUST", message=None):
            """Create an StructuralRequirement from values supplied."""
            return cls(req_id, level, message)

        @staticmethod
        def _get_struct_reqs():
            reqs = []
            for req_num in STRUCT_REQS:
                req = STRUCT_REQS.get(req_num)
                reqs.append(Specification.StructuralRequirement(req.get('id'),
                                                                level=req.get('level'),
                                                                message=req.get('message')))
            return reqs
