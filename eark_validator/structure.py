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
from enum import Enum, unique
import os
import tarfile
import tempfile
import zipfile

from eark_validator.rules import Severity
import eark_validator.specifications.specification as SPECS

from eark_validator.infopacks.manifest import Checksum

MD_DIR = 'metadata'
REPS_DIR = 'representations'
SCHEMA_DIR = 'schemas'
METS_NAME = 'METS.xml'
STR_REQ_PREFIX = 'CSIPSTR'
SUB_MESS_NOT_EXIST = 'Path {} does not exist'
SUB_MESS_NOT_ARCH = 'Path {} is not a directory or archive format file.'
# Map requirement levels to severity
LEVEL_SEVERITY = {
    'MUST': Severity.ERROR,
    'SHOULD': Severity.WARN,
    'MAY': Severity.INFO
}
@unique
class StructureStatus(Enum):
    """Enum covering information package validation statuses."""
    Unknown = 'Unknown'
    # Package has basic parse / structure problems and can't be validated
    NotWellFormed = 'Not Well Formed'
    # Package structure is OK
    WellFormed = 'Well Formed'

class StructureReport:
    """Stores the vital facts and figures about a package."""
    structure_values = list(StructureStatus)
    def __init__(self, status: StructureStatus=StructureStatus.Unknown, errors: list[str]=None, warnings: list[str]=None, infos: list[str]=None):
        self.status = status
        self._errors = errors if errors else []
        self._warnings = warnings if warnings else []
        self._infos = infos if infos else []

    @property
    def status(self) -> StructureStatus:
        """Get the structure status."""
        return self._status

    @status.setter
    def status(self, value: StructureStatus) -> None:
        if value not in self.structure_values:
            raise ValueError('Illegal package status value')
        self._status = value

    @property
    def errors(self) -> list[str]:
        """Return the full list of error messages."""
        return self._errors

    @property
    def warnings(self) -> list[str]:
        """Return the full list of warnings messages."""
        return self._warnings

    @property
    def infos(self) -> list[str]:
        """Return the full list of info messages."""
        return self._infos

    @property
    def messages(self):
        """Generator that yields all of the messages in the report."""
        for entry in self.errors:
            yield entry
        for entry in self.warnings:
            yield entry
        for entry in self.infos:
            yield entry

    def add_error(self, error: str) -> None:
        """Add a validation error to package lists."""
        if error.severity == Severity.INFO:
            self._infos.append(error)
        elif error.severity == Severity.WARN:
            self._warnings.append(error)
        elif error.severity == Severity.ERROR:
            self._errors.append(error)
            self.status = StructureStatus.NotWellFormed

    def add_errors(self, errors: list[str]) -> None:
        """Add a validation error to package lists."""
        for error in errors:
            self.add_error(error)

    @classmethod
    def from_path(cls, path: str) -> 'StructureReport':
        """Create a structure report from a path, this can be a folder or an archive file."""
        rep = StructureReport(status=StructureStatus.WellFormed)
        root = path
        if not os.path.exists(path):
            # If it doesn't exist then add an error message
            rep.add_error(StructError.from_rule_no(1, sub_message=SUB_MESS_NOT_EXIST.format(path)))
        elif os.path.isfile(path):
            if ArchivePackageHandler.is_archive(path):
                root = cls._handle_archive(path)
            else:
                rep.add_error(StructError.from_rule_no(1,
                                                     sub_message=SUB_MESS_NOT_ARCH.format(path)))

        struct_checker = StructureChecker.from_directory(root)
        rep.add_errors(struct_checker.validate_manifest())
        reps_dir = os.path.join(root, REPS_DIR)
        if os.path.isdir(reps_dir):
            for entry in os.listdir(reps_dir):
                struct_checker = StructureChecker.from_directory(os.path.join(reps_dir, entry))
                rep.add_errors(struct_checker.validate_manifest(is_root=False))
        return rep

    @classmethod
    def _handle_archive(cls, archive_path: str) -> str:
        arch_handler = ArchivePackageHandler()
        root = arch_handler.unpack_package(archive_path)
        if len(os.listdir(root)) == 1:
            for entry in os.listdir(root):
                ent_path = os.path.join(root, entry)
                if os.path.isdir(ent_path):
                    root = ent_path
        return root


    def __str__(self):
        return 'status:' + str(self.status)

class StructError():
    """Encapsulates an individual validation test result."""
    def __init__(self, requirement: str, sub_message: str):
        self._requirement = requirement
        self.severity = LEVEL_SEVERITY.get(requirement.level, Severity.UNKNOWN)
        self._sub_message = sub_message

    @property
    def id(self) -> str: # pylint: disable-msg=C0103
        """Get the rule_id."""
        return self._requirement.id

    @property
    def severity(self) -> Severity:
        """Get the severity."""
        return self._severity

    @severity.setter
    def severity(self, value: Severity) -> None:
        if value not in list(Severity):
            raise ValueError('Illegal severity value')
        self._severity = value

    @property
    def is_error(self) -> bool:
        """Returns True if this is an error message, false otherwise."""
        return self.severity == Severity.ERROR

    @property
    def is_info(self) -> bool:
        """Returns True if this is an info message, false otherwise."""
        return self.severity == Severity.INFO

    @property
    def is_warning(self) -> bool:
        """Returns True if this is an warning message, false otherwise."""
        return self.severity == Severity.WARN

    @property
    def message(self) -> str:
        """Get the message."""
        return self._requirement.message

    @property
    def sub_message(self) -> str:
        """Get the sub-message."""
        return self._sub_message

    def to_json(self) -> dict:
        """Output the message in JSON format."""
        return {'id' : self.id, 'severity' : str(self.severity.name),
                'message' : self.message, 'sub_message' : self.sub_message}

    def __str__(self) -> str:
        return 'id:{}, severity:{}, message:{}, sub_message:{}'.format(self.id,
                                                                       str(self.severity.name),
                                                                       self.message,
                                                                       self.sub_message)
    @classmethod
    def from_rule_no(cls, rule_no: int, sub_message: str=None) -> 'StructError':
        """Create an StructError from values supplied."""
        requirement = SPECS.Specification.StructuralRequirement.from_rule_no(rule_no)
        return StructError(requirement, sub_message)

    @classmethod
    def from_values(cls, requirement: str, sub_message: str=None) -> 'StructError':
        """Create an StructError from values supplied."""
        return StructError(requirement, sub_message)

class ArchivePackageHandler():
    """Class to handle archive / compressed information packages."""
    def __init__(self, unpack_root: str=tempfile.gettempdir()):
        self._unpack_root = unpack_root

    @property
    def unpack_root(self) -> str:
        """Returns the root directory for archive unpacking."""
        return self._unpack_root

    def unpack_package(self, to_unpack: str, dest: str=None) -> str:
        """Unpack an archived package to a destination (defaults to tempdir).
        returns the destination folder."""
        if not os.path.isfile(to_unpack) or not self.is_archive(to_unpack):
            raise PackageStructError('File is not an archive file.')
        sha1 = Checksum.from_file(to_unpack, 'sha1')
        dest_root = dest if dest else self.unpack_root
        destination = os.path.join(dest_root, sha1.value)
        if zipfile.is_zipfile(to_unpack):
            zip_ip = zipfile.ZipFile(to_unpack)
            zip_ip.extractall(path=destination)
        elif tarfile.is_tarfile(to_unpack):
            tar_ip = tarfile.open(to_unpack)
            tar_ip.extractall(path=destination)
        return destination

    @staticmethod
    def is_archive(to_test: str) -> bool:
        """Return True if the file is a recognised archive type, False otherwise."""
        if zipfile.is_zipfile(to_test):
            return True
        return tarfile.is_tarfile(to_test)

def validate_package_structure(package_path: str) -> StructureReport:
    """Carry out all structural package tests."""
    # It's a file so we need to unpack it
    return StructureReport.from_path(package_path)

class StructureChecker():
    """Encapsulate the mess that is the manifest details."""
    def __init__(self, name, has_mets=True, has_md=True, has_schema=True,
                 has_data=False, has_reps=True):
        self.name = name
        self.has_mets = has_mets
        self.has_md = has_md
        self.has_schema = has_schema
        self.has_data = has_data
        self.has_reps = has_reps

    def validate_manifest(self, is_root: bool=True) -> list[StructError]:
        """Validate a manifest report and return the list of validation errors."""
        validation_errors = []
        # [CSIPSTR4] Is there a file called METS.xml (perform case checks)
        # [CSIPSTR12] Does each representation folder have a METS.xml file? (W)
        if not self.has_mets:
            if is_root:
                validation_errors.append(StructError.from_rule_no(4))
            else:
                validation_errors.append(StructError.from_rule_no(12))
        # [CSIPSTR5] Is there a first level folder called metadata?
        # [CSIPSTR13] Does each representation folder have a metadata folder (W)
        if not self.has_md:
            if is_root:
                validation_errors.append(StructError.from_rule_no(5))
            else:
                validation_errors.append(StructError.from_rule_no(13))
        # [CSIPSTR15] Is there a schemas folder at the root level/representations? (W)
        if not self.has_schema:
            validation_errors.append(StructError.from_rule_no(15))
        # [CSIPSTR11] Does each representation folder have a sub folder called data? (W)
        if not self.has_data and not is_root:
            validation_errors.append(StructError.from_rule_no(11))
        # [CSIPSTR9] Is there a first level folder called representations (W)
        if not self.has_reps and is_root:
            validation_errors.append(StructError.from_rule_no(9))
        return validation_errors

    @classmethod
    def from_directory(cls, dir_to_scan: str) -> 'StructureChecker':
        """Create a manifest instance from a directory."""
        has_mets = False
        has_md = False
        has_schema = False
        has_data = False
        has_reps = False
        name = os.path.basename(dir_to_scan)
        for entry in os.listdir(dir_to_scan):
            entry_path = os.path.join(dir_to_scan, entry)
            # [CSIPSTR4] Is there a file called METS.xml (perform case checks)
            # [CSIPSTR12] Does each representation folder have a METS.xml file? (W)
            if entry == METS_NAME:
                if os.path.isfile(entry_path):
                    has_mets = True
            # [CSIPSTR5] Is there a first level folder called metadata?
            # [CSIPSTR13] Does each representation folder have a metadata folder (W)
            if os.path.isdir(entry_path):
                if entry == 'metadata':
                    has_md = True
                # [CSIPSTR15] Is there a schemas folder at the root level/representations? (W)
                elif entry == 'schemas':
                    has_schema = True
                # [CSIPSTR11] Does each representation folder have a sub folder called data? (W)
                elif entry == 'data':
                    has_data = True
                # [CSIPSTR9] Is there a first level folder called representations (W)
                elif entry == REPS_DIR:
                    has_reps = True
        return StructureChecker(name, has_mets, has_md, has_schema, has_data, has_reps)

class PackageStructError(RuntimeError):
    """Exception to signal fatal pacakge structure errors."""
    def __init__(self, arg):
        super().__init__()
        self.args = arg
