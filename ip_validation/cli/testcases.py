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
import os.path

import lxml.etree as ET

from importlib_resources import files

import ip_validation.cli.resources as RES
import ip_validation.infopacks.structure as STRUCT

from ip_validation.infopacks.mets import MetsValidator
from ip_validation.infopacks.rules import ValidationProfile

DEFAULT_NAME='testCase.xml'
TC_SCHEMA = ET.XMLSchema(file=str(files(RES).joinpath('testCase.xsd')))

class TestCase():
    """
    Encapsulates the E-ARK XML Test Case files.

    Parameters / attributes
     - case_id: a CaseId instance that is the compound test case id.
     - testable: boolean, True if test case is "testable", False otherwise
     - references: a list of references to relavent requirements.
    """
    def __init__(self, case_id, details, valid, testable=True,
                 rules=None):
        self._case_id = case_id
        self._valid = valid
        self._details = details
        self._testable = testable
        self._rules = [] if rules is None else rules

    @property
    def case_id(self):
        """Return the test case id instance."""
        return self._case_id

    @property
    def valid(self):
        """Return True if the test case is valid XML against the schema supplied."""
        return self._valid

    @property
    def description(self):
        """Return the test case description."""
        return self._details.description

    @property
    def testable(self):
        """Return True if the test case is considered testable, otherwise False."""
        return self._testable == 'TRUE'

    @property
    def unknown(self):
        """Return True if the test case testability is unknown, otherwise False."""
        return self._testable == 'UNKNOWN'

    @property
    def status(self):
        """Return the test case status."""
        return self._testable

    @property
    def references(self):
        """Return the list of relavent requirements."""
        return self._details.references

    @property
    def requirement(self):
        """Return the requirement."""
        return self._details.requirement

    @property
    def rules(self):
        """Return the rules associated with the test case."""
        return self._rules

    def resolve_package_paths(self, case_root):
        """Resolve package paths for all rule packages."""
        for rule in self.rules:
            for package in rule.packages:
                package.resolve_path(case_root)

    def validate_packages(self):
        """Validate all of a test cases packages."""
        for rule in self.rules:
            rule.validate_packages()

    @property
    def package_count(self):
        """Return the number of packages in the test case."""
        count = 0
        for rule in self.rules:
            count+=len(rule.packages)
        return count

    @property
    def missing_package_count(self):
        """Return the number of packages in the test case."""
        count = 0
        for rule in self.rules:
            count+=len(rule.missing_packages)
        return count

    def __str__(self):
        return "case_id:" + str(self.case_id) + ", testable:" + \
            str(self.testable)

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
            return self._specification

        @property
        def version(self):
            """Return the version."""
            return self._version

        @classmethod
        def from_element(cls, case_id_ele):
            """Create a TestCase from an XML element."""
            requirement_id = case_id_ele.get('requirementId')
            specification = case_id_ele.get('specification')
            specification = specification[len('E-ARK '):] \
                if specification.startswith('E-ARK ') else specification
            version = case_id_ele.get('version')
            return cls(requirement_id, specification, version)

        def __str__(self):
            return "req_id:" + str(self.requirement_id) + ", specification:" + \
                str(self.specification) + ", version:" + str(self.version)

    class CaseDetails():
        """
        Encapsulates the details of an E-ARK test case.

        Parameters / attributes
         - case_id: a CaseId instance that is the compound test case id.
         - testable: boolean, True if test case is "testable", False otherwise
         - references: a list of references to relavent requirements.
        """
        def __init__(self, requirement, description, references=None):
            self._req = requirement
            self._description = description
            self._references = [] if references is None else references

        @property
        def requirement(self):
            """Return the requirement."""
            return self._req

        @property
        def description(self):
            """Return the test case description."""
            return self._description

        @property
        def references(self):
            """Return the list of relavent requirements."""
            return self._references

        def __str__(self):
            return "requirement:" + self.requirement + ", description:" + \
                self.description


    class Rule():
        """docstring for Rule."""
        def __init__(self, rule_id, description, error, packages):
            self._rule_id = rule_id
            self._description = description
            self._error = error
            self._packages = packages

        @property
        def rule_id(self):
            """Return the rule ID."""
            return self._rule_id

        @property
        def description(self):
            """Return the description."""
            return self._description

        @property
        def error(self):
            """Return the error."""
            return self._error

        @property
        def packages(self):
            """Return the corpus packages."""
            return self._packages

        @property
        def missing_packages(self):
            """Return a list of missing packages."""
            missing = []
            for package in self.packages:
                if not package.exists:
                    missing.append(package)
            return missing

        @property
        def existing_packages(self):
            """Return a list of existing packages."""
            existing = []
            for package in self.packages:
                if package.exists:
                    existing.append(package)
            return existing

        def resolve_package_paths(self, case_root):
            """Resolve package paths for all rule packages."""
            for package in self.packages:
                package.resolve_path(case_root)

        def validate_packages(self):
            """Validate all packages in a rule."""
            for package in self.packages:
                package.validate()

        def __str__(self):
            return "rule_id:" + self.rule_id + ", description:" + \
                self.description + ", error:" + str(self.error)

        @classmethod
        def from_element(cls, rule_ele):
            """Create a Rule from an XML element."""
            rule_id = rule_ele.get('id')
            description = ""
            error = None
            packages = []
            for child in rule_ele:
                if child.tag == 'description':
                    description = child.text
                elif child.tag == 'error':
                    error = cls.Error.from_element(child)
                elif child.tag == 'corpusPackages':
                    packages = cls._parse_package_list(child)
            return cls(rule_id, description, error, packages)

        @staticmethod
        def _parse_package_list(packages_ele):
            packages = []
            for child in packages_ele:
                if child.tag == 'package':
                    packages.append(TestCase.Rule.Package.from_element(child))
            return packages

        class Error():
            """docstring for Error."""
            def __init__(self, level, message):
                self._level = level
                self._message = message

            @property
            def level(self):
                """Return the level."""
                return self._level

            @property
            def message(self):
                """Return the message."""
                return self._message

            def __str__(self):
                return 'level: {}, message {}'.format(self.level, self.message)

            @classmethod
            def from_element(cls, error_ele):
                """Return a Errpr instance from an XML element."""
                level = error_ele.get('level')
                message = ''
                for child in error_ele:
                    if child.tag == 'message':
                        message = child.text
                return cls(level, message)

        class Package():
            """docstring for Package."""
            def __init__(self, name, path, is_valid, is_implemented, description, validation_report=None):
                self._name = name
                self._path = path
                self._is_valid = is_valid
                self._description = description
                self._validation_report = validation_report
                self.schema_result = False
                self.schematron_result = False
                self.profile_results = {}
                self.exists = False

            @property
            def name(self):
                """Return the name."""
                return self._name

            @property
            def path(self):
                """Return the path."""
                return self._path

            def resolve_path(self, case_root):
                """Resolve the path to the corpus package given the test case root."""
                print('Resolving: {}'.format(self.path))
                if self.path:
                    self._path = os.path.join(case_root, self.name)
                    if not self.exists:
                        self._path = os.path.join(case_root, self.path)
                return self.path

            @property
            def exists(self):
                """Return True if the package can be found in the git repo."""
                return self.__exists

            @exists.setter
            def exists(self, exists):
                """Check if the corpus package exists given the test case root."""
                self.__exists = exists

            @property
            def is_valid(self):
                """Return the is_valid."""
                return self._is_valid

            @property
            def implemented(self):
                """Return True if the test case is valid XML against the schema supplied."""
                return self._is_implemented

            @property
            def description(self):
                """Return the description."""
                return self._description

            @property
            def validation_report(self):
                """Return the validation report for the package."""
                return self._validation_report

            @property
            def validation_result(self):
                """Return the validation report for the package."""
                return self._validation_report.status == STRUCT.StructureStatus.WellFormed and \
                    self.schema_result and self.schematron_result

            def __str__(self):
                return 'name: {}, path: {}'.format(self.name, self.path)

            def validate(self):
                """Validate the package."""
                if self.exists:
                    profile = ValidationProfile()
                    struct_report = STRUCT.validate_package_structure(self.path)
                    # IF package is well formed then we can validate it.
                    if struct_report.status == STRUCT.StructureStatus.WellFormed:
                        # Schema based METS validation first
                        validator = MetsValidator(self.path)
                        mets_path = os.path.join(self.path, 'METS.xml')
                        self.schema_result = validator.validate_mets(mets_path)
                        # Now grab any errors
                        if self.schema_result is True:
                            profile.validate(mets_path)
                            self.profile_results = profile.get_results()
                            self.schematron_result=profile.is_valid
                    self._validation_report = STRUCT.validate_package_structure(self.path)

            @classmethod
            def from_element(cls, package_ele):
                """Return a Package instance from an XML element."""
                is_valid = package_ele.get('isValid')
                is_implemented = package_ele.get('isImplemented')
                name = package_ele.get('name')
                path = ""
                description = ""
                for child in package_ele:
                    if child.tag == 'path':
                        path = child.text
                    elif child.tag == 'description':
                        description = child.text
                return cls(name, path, is_valid, is_implemented, description)

    @classmethod
    def from_xml_string(cls, xml, schema=TC_SCHEMA):
        """Create a test case from an XML string."""
        try:
            ele = ET.fromstring(xml)
        except ET.XMLSyntaxError as xml_excep:
            raise ValueError('String parameter "xml" not valid test case XML.') from xml_excep
        return cls.from_element(ele, schema)

    @classmethod
    def from_xml_file(cls, xml_file, schema=TC_SCHEMA):
        """Create a test case from an XML file."""
        tree = ET.parse(xml_file)
        return  cls._from_xml(tree, schema)

    @classmethod
    def _from_xml(cls, tree, schema):
        return cls.from_element(tree.getroot(), schema)

    @classmethod
    def from_element(cls, case_ele, schema):
        """Create a TestCase from an XML element."""
        # Grab the testable att
        if not schema.validate(case_ele):
            details = TestCase.CaseDetails(None, str(schema.error_log.last_error))
            return cls(None, details, False)
        testable = case_ele.get('testable')
        req_id = None
        req = None
        description = None
        rules = []
        # Loop through the child eles
        for child in case_ele:
            if child.tag == 'id':
                # Process the id element
                req_id = cls.CaseId.from_element(child)
            elif child.tag == 'requirementText':
                # Grab the requirement text value
                req = child.text
            elif child.tag == 'description':
                # Grab the requirement text value
                description = child.text
            elif child.tag == 'rules':
                for rule_ele in child:
                    if rule_ele.tag == 'rule':
                        rules.append(cls.Rule.from_element(rule_ele))

        # Return the TestCase instance
        details = TestCase.CaseDetails(req, description)
        return cls(req_id, details, True, testable=testable, rules=rules)

class GitTestCase():
    """A wrapper around test cases held in a git repository."""
    def __init__(self, ref, path, test_case):
        self._ref = ref
        self._path = path
        self._tc = test_case

    @property
    def ref(self):
        """Return the git reference for this test case."""
        return self._ref

    @property
    def root(self):
        """Return the root path for this test case."""
        return self._path.parent

    @property
    def path(self):
        """Return the git path for this test case."""
        return self._path

    @property
    def test_case(self):
        """Return the test case."""
        return self._tc

    @property
    def case_id(self):
        """Return the test case id instance."""
        return self._tc.case_id

    @property
    def valid(self):
        """Return True if the test case is valid XML against the schema supplied."""
        return self._tc.valid

    @property
    def description(self):
        """Return the test case description."""
        return self._tc.details.description

    @property
    def testable(self):
        """Return True if the test case is considered testable, otherwise False."""
        return self._tc.testable

    @property
    def unknown(self):
        """Return True if the test case testability is unknown, otherwise False."""
        return self._tc.unknown

    @property
    def status(self):
        """Return the test case status."""
        return self._tc.status

    @property
    def references(self):
        """Return the list of relavent requirements."""
        return self._tc.details.references

    @property
    def requirement(self):
        """Return the requirement."""
        return self._tc.details.requirement

    @property
    def rules(self):
        """Return the rules associated with the test case."""
        return self._tc.rules

    @property
    def package_count(self):
        """Return the number of packages in the test case."""
        return self._tc.package_count

    @property
    def missing_package_count(self):
        """Return the number of packages in the test case."""
        return self._tc.missing_package_count

    def __str__(self):
        return 'ref:' + str(self.ref) + ', path:' + str(self.path) \
            + ', case:' + str(self.test_case)
