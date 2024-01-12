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
"""Encapsulates all things related to information package structure."""
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from eark_validator.specifications.struct_reqs import REQUIREMENTS
from eark_validator.infopacks.package_handler import PackageHandler, PackageError
from eark_validator.model import (
    StructResults,
    StructureStatus,
    TestResult,
    Severity,
    Representation
)

METS_NAME = 'METS.xml'
STR_REQ_PREFIX = 'CSIPSTR'
DIR_NAMES = {
    'DATA': 'data',
    'DESC': 'descriptive',
    'DOCS': 'documentation',
    'META': 'metadata',
    'OTHR': 'other',
    'PRES': 'preservation',
    'REPS': 'representations',
    'SCHM': 'schemas'
}

class StructureParser():
    _package_handler = PackageHandler()
    """Encapsulates the set of tests carried out on folder structure."""
    def __init__(self, package_path: Path):
        self._is_archive = package_path.is_file() and PackageHandler.is_archive(package_path)
        to_process = self._package_handler.prepare_package(package_path)
        self.folders, self.files = _folders_and_files(to_process)
        if DIR_NAMES['META'] in self.folders:
            self.md_folders, _ = _folders_and_files(os.path.join(to_process, DIR_NAMES['META']))
        else:
            self.md_folders = set()

    def has_data(self) -> bool:
        """Returns True if the package/representation has a structure folder."""
        return DIR_NAMES['DATA'] in self.folders

    def has_descriptive_md(self) -> bool:
        """Returns True if the package/representation has a descriptive metadata folder."""
        return DIR_NAMES['DESC'] in self.md_folders

    def has_documentation(self) -> bool:
        """Returns True if the package/representation has a documentation folder."""
        return DIR_NAMES['DOCS'] in self.folders

    def has_mets(self) -> bool:
        """Returns True if the package/representation has a root METS.xml file."""
        return METS_NAME in self.files

    def has_metadata(self) -> bool:
        """Returns True if the package/representation has a metadata folder."""
        return DIR_NAMES['META'] in self.folders

    def has_other_md(self) -> bool:
        """Returns True if the package/representation has extra metadata folders
        after preservation and descriptive."""
        md_folder_count = len(self.md_folders)
        if self.has_preservation_md():
            md_folder_count-=1
        if self.has_descriptive_md():
            md_folder_count-=1
        return md_folder_count > 0

    def has_preservation_md(self) -> bool:
        """Returns True if the package/representation has a preservation metadata folder."""
        return DIR_NAMES['PRES'] in self.md_folders

    def has_representations(self) -> bool:
        """Returns True if the package/representation has a representations folder."""
        return DIR_NAMES['REPS'] in self.folders

    def has_schemas(self) -> bool:
        """Returns True if the package/representation has a schemas folder."""
        return DIR_NAMES['SCHM'] in self.folders

    @property
    def is_archive(self) -> bool:
        """Returns True if the package/representation is an archive."""
        return self._is_archive

class StructureChecker():
    def __init__(self, dir_to_scan: Path):
        self.name: Path = os.path.basename(dir_to_scan)
        self.parser: StructureParser = StructureParser(dir_to_scan)
        self.representations: Dict[Representation, StructureParser] = {}
        _reps = os.path.join(dir_to_scan, DIR_NAMES['REPS'])
        if os.path.isdir(_reps):
            for entry in  os.listdir(_reps):
                self.representations[entry] = StructureParser(Path(os.path.join(_reps, entry)))

    def get_test_results(self) -> StructResults:
        results: List[TestResult] = self.get_root_results()
        results = results + self.get_package_results()

        for name, tests in self.representations.items():
            location = 'Representation {}'.format(name)
            if not tests.has_data():
                results.append(test_result_from_id(11, location))
            if not tests.has_mets():
                results.append(test_result_from_id(12, location))
            if not tests.has_metadata():
                results.append(test_result_from_id(13, location))
        return StructResults(status=self.get_status(results), messages=results)

    def get_representations(self) -> List[Representation]:
        reps: List[Representation] = []
        for rep in self.representations.keys():
            reps.append(Representation(name=rep))
        return reps

    def get_root_results(self) -> List[TestResult]:
        results: List[TestResult] = []
        if not self.parser.is_archive:
            results.append(test_result_from_id(3, self.name))
        if not self.parser.has_mets():
            results.append(test_result_from_id(4, self.name))
        if not self.parser.has_metadata():
            results.append(test_result_from_id(5, self.name))
        if not self.parser.has_preservation_md():
            results.append(test_result_from_id(6, self.name))
        if not self.parser.has_descriptive_md():
            results.append(test_result_from_id(7, self.name))
        if not self.parser.has_other_md():
            results.append(test_result_from_id(8, self.name))
        if not self.parser.has_representations():
            results.append(test_result_from_id(9, self.name))
        return results

    def get_package_results(self) -> List[TestResult]:
        results: List[TestResult] = []
        if not self.parser.has_schemas():
            result = self._get_schema_results()
            if result:
                results.append(result)
        if not self.parser.has_documentation():
            result = self._get_dox_results()
            if result:
                results.append(result)
        return results

    def _get_schema_results(self) -> Optional[TestResult]:
        for tests in self.representations.values():
            if tests.has_schemas():
                return None
        return test_result_from_id(15, self.name)

    def _get_dox_results(self) -> Optional[TestResult]:
        for tests in self.representations.values():
            if tests.has_documentation():
                return None
        return test_result_from_id(16, self.name)

    @classmethod
    def get_status(cls, results: List[TestResult]) -> StructureStatus:
        for result in results:
            if result.severity == Severity.Error:
                return StructureStatus.NotWellFormed
        return StructureStatus.WellFormed

def _folders_and_files(dir_to_scan: Path) -> Tuple[Set[str], Set[str]]:
    folders: Set[str] = set()
    files: Set[str] = set()
    if os.path.isdir(dir_to_scan):
        for entry in os.listdir(dir_to_scan):
            path = os.path.join(dir_to_scan, entry)
            if os.path.isfile(path):
                files.add(entry)
            elif os.path.isdir(path):
                folders.add(entry)
    return folders, files

def test_result_from_id(requirement_id, location, message=None) -> TestResult:
    req = REQUIREMENTS[requirement_id]
    test_msg = message if message else req['message']
    """Return a TestResult instance created from the requirment ID and location."""
    return TestResult(rule_id=req['id'], location=str(location), message=test_msg, severity=Severity.from_level(req['level']))

def get_multi_root_results(name) -> StructResults:
    return StructResults(status=StructureStatus.NotWellFormed, messages=[ test_result_from_id(1, name) ])

def get_bad_path_results(path) -> StructResults:
    return StructResults(status=StructureStatus.NotWellFormed, messages=[ test_result_from_id(1, path) ])

def validate(to_validate) -> Tuple[bool, StructResults]:
    try:
        struct_tests = StructureChecker(to_validate).get_test_results()
        return struct_tests.status == StructureStatus.WellFormed, struct_tests
    except PackageError:
        return False, get_multi_root_results(to_validate)
