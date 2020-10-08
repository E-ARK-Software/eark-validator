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
        E-ARK Test Case processing
"""
import xml.etree.ElementTree as ET

class TestCase():
    """
    Encapsulates the E-ARK XML Test Case files.

    Parameters / attributes
     - case_id: a CaseId instance that is the compound test case id.
     - testable: boolean, True if test case is "testable", False otherwise
     - references: a list of references to relavent requirements.
    """
    def __init__(self, case_id, testable=True, references=None, text=""):
        self._case_id = case_id
        self._testable = testable
        if references is None:
            references = []
        self._references = references
        self._text = text

    @property
    def case_id(self):
        """Return the test case id instance."""
        return self._case_id

    @property
    def testable(self):
        """Return True if the test case is considered testable, otherwise False."""
        return self._testable == 'TRUE'

    @property
    def references(self):
        """Return the list of relavent requirements."""
        return self._references

    @property
    def requirement_text(self):
        """Return the requirment text."""
        return self._text

    class CaseId():
        """
        Encapsulates an E-ARK XML Test Case ID.

        Parameters / attributes
         - requirement_id: a requirement ID string from the specification.
         - specification: the name of the specification.
         - version: the version of the specifciation.
        """
        def __init__(self, requirement_id, specification="CSIP", version="2.0"):
            self._requirement_id = requirement_id
            self._specification = specification
            self._version = version

        @property
        def requirement_id(self):
            """Return the requirement ID."""
            return self._requirement_id

        @property
        def specification(self):
            """Return the specification name."""
            return self._requirement_id

        @property
        def version(self):
            """Return the version."""
            return self._version

        @classmethod
        def from_element(cls, case_id_ele):
            """Create a TestCase from an XML element."""
            requirement_id = case_id_ele.get('requirementId')
            specification = case_id_ele.get('specification')
            version = case_id_ele.get('version')
            return cls(requirement_id, specification, version)

    @classmethod
    def from_xml_string(cls, xml):
        """Create a test case from an XML string."""
        tree = ET.fromstring(xml)
        return cls.from_element(tree.getroot())

    @classmethod
    def from_xml_file(cls, xml_file):
        """Create a test case from an XML file."""
        tree = ET.parse(xml_file)
        return cls.from_element(tree.getroot())

    @classmethod
    def from_element(cls, case_ele):
        """Create a TestCase from an XML element."""
        # Grab the testable att
        testable = case_ele.get('testable')
        req_id = None
        text = ""
        # Loop through the child eles
        for child in case_ele:
            if child.tag == 'id':
                # Process the id element
                req_id = cls.CaseId.from_element(child)
            elif child.tag == 'requirementText':
                # Grab the requirement text value
                text = child.text
        # Return the TestCase instance
        return cls(req_id, testable=testable, text=text)
