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
"""Encapsulates all things related to information package structure."""
from enum import Enum, unique
import os
import tarfile
import tempfile
import zipfile

from ip_validation.infopacks.rules import Severity
import ip_validation.utils as UTILS

MD_DIR = "metadata"
REPS_DIR = "representations"
SCHEMA_DIR = "schemas"
METS_NAME = 'METS.xml'

# Simple definition of package structure errors.
STRUCT_ERRORS = {
    1: """Any Information Package MUST be included within a single physical root
       folder (known as the “Information Package root folder”). For packages
       presented in an archive format, see CSIPSTR3, the archive MUST unpack to
       a single root folder.""",
    2: """The Information Package root folder SHOULD be named with the ID or
       name of the Information Package, that is the value of the package
       METS.xml’s root <mets> element’s @OBJID attribute.""",
    3: """The Information Package root folder MAY be compressed (for example by
       using TAR or ZIP). Which specific compression format to use needs to be
       stated in the Submission Agreement.""",
    4: """The Information Package root folder MUST include a file named
       METS.xml. This file MUST contain metadata that identifies the package,
       provides a high-level package description, and describes its structure,
       including pointers to constituent representations.""",
    5: """The Information Package root folder SHOULD include a folder named
       metadata, which SHOULD include metadata relevant to the whole package.""",
    6: """If preservation metadata are available, they SHOULD be included in
       sub-folder preservation.""",
    7: """If descriptive metadata are available, they SHOULD be included in
       sub-folder descriptive.""",
    8: """If any other metadata are available, they MAY be included in
       separate sub-folders, for example an additional folder named other.""",
    9: """The Information Package folder SHOULD include a folder named
       representations.""",
    10: """The representations folder SHOULD include a sub-folder for each
        individual representation (i.e. the “representation folder”). Each
        representation folder should have a string name that is unique within
        the package scope. For example the name of the representation and/or its
        creation date might be good candidates as a representation sub-folder
        name.""",
    11: """The representation folder SHOULD include a sub-folder named data
        which MAY include all data constituting the representation.""",
    12: """The representation folder SHOULD include a metadata file named
        METS.xml which includes information about the identity and structure of
        the representation and its components. The recommended best practice is
        to always have a METS.xml in the representation folder.""",
    13: """The representation folder SHOULD include a sub-folder named metadata
        which MAY include all metadata about the specific representation.""",
    14: """The Information Package MAY be extended with additional sub-folders.""",
    15: """We recommend including all XML schema documents for any structured
        metadata within package. These schema documents SHOULD be placed in a
        sub-folder called schemas within the Information Package root folder
        and/or the representation folder.""",
    16: """We recommend including any supplementary documentation for the
        package or a specific representation within the package. Supplementary
        documentation SHOULD be placed in a sub-folder called documentation
        within the Information Package root folder and/or the representation
        folder."""
}
SUB_MESS_NOT_EXIST = 'Path {} does not exist'
SUB_MESS_NOT_ARCH = 'Path {} is not a directory or archive format file.'

@unique
class StructureStatus(Enum):
    """Enum covering information package validation statuses."""
    Unknown = 1
    # Package has basic parse / structure problems and can't be validated
    NotWellFormed = 2
    # Package structure is OK
    WellFormed = 3


class StructureReport:
    """Stores the vital facts and figures about a package."""
    structure_values = list(StructureStatus)
    def __init__(self, status=StructureStatus.Unknown, errors=None, warnings=None, infos=None):
        self.status = status
        self._errors = errors if errors else []
        self._warnings = warnings if warnings else []
        self._infos = infos if infos else []

    @property
    def status(self):
        """Get the structure status."""
        return self._status

    @status.setter
    def status(self, value):
        if not value in self.structure_values:
            raise ValueError("Illegal package status value")
        self._status = value

    @property
    def errors(self):
        """Return the full list of error messages."""
        return self._errors

    @property
    def warnings(self):
        """Return the full list of warnings messages."""
        return self._warnings

    @property
    def infos(self):
        """Return the full list of info messages."""
        return self._infos

    @property
    def messages(self):
        for entry in self.errors:
            yield entry
        for entry in self.warnings:
            yield entry
        for entry in self.infos:
            yield entry

    def add_error(self, error):
        """Add a validation error to package lists."""
        if error.severity == Severity.Info:
            self._infos.append(error)
        elif error.severity == Severity.Warn:
            self._warnings.append(error)
        elif error.severity == Severity.Error:
            self._errors.append(error)
            self.status = StructureStatus.NotWellFormed

    def add_errors(self, errors):
        """Add a validation error to package lists."""
        for error in errors:
            self.add_error(error)

    @classmethod
    def from_path(cls, path):
        """Create a structure report from a path, this can be a folder or an archive file."""
        rep = StructureReport(status=StructureStatus.WellFormed)
        root = path
        if not os.path.exists(path):
            # If it doesn't exist then add an error message
            rep.add_error(StructError.from_values(1, severity=Severity.Error,
                                                     sub_message=SUB_MESS_NOT_EXIST.format(path)))
        elif os.path.isfile(path):
            if ArchivePackageHandler.is_archive(path):
                arch_handler = ArchivePackageHandler()
                root = arch_handler.unpack_package(path)
                if len(os.listdir(root)) == 1:
                    for entry in os.listdir(root):
                        ent_path = os.path.join(root, entry)
                        if os.path.isdir(ent_path):
                            root = ent_path
            else:
                rep.add_error(StructError.from_values(1, severity=Severity.Error,
                                                      sub_message=SUB_MESS_NOT_ARCH.format(path)))

        struct_checker = StructureChecker.from_directory(root)
        rep.add_errors(struct_checker.validate_manifest())
        reps_dir = os.path.join(root, REPS_DIR)
        if os.path.isdir(reps_dir):
            for entry in os.listdir(reps_dir):
                struct_checker = StructureChecker.from_directory(os.path.join(reps_dir, entry))
                rep.add_errors(struct_checker.validate_manifest(is_root=False))
        return rep

    def __str__(self):
        return "status:" + str(self.status)

class StructError():
    """Encapsulates an individual validation test result."""
    def __init__(self, rule_id, severity, message, sub_message):
        self._rule_id = rule_id
        self.severity = severity
        self._message = message
        self._sub_message = sub_message

    @property
    def rule_id(self):
        """Get the rule_id."""
        return self._rule_id

    @property
    def severity(self):
        """Get the severity."""
        return self._severity

    @severity.setter
    def severity(self, value):
        if not value in list(Severity):
            raise ValueError("Illegal severity value")
        self._severity = value

    @property
    def is_error(self):
        """Returns True if this is an error message, false otherwise."""
        return self.severity == Severity.Error

    @property
    def is_info(self):
        """Returns True if this is an info message, false otherwise."""
        return self.severity == Severity.Info

    @property
    def is_warning(self):
        """Returns True if this is an warning message, false otherwise."""
        return self.severity == Severity.Warn

    @property
    def message(self):
        """Get the message."""
        return self._message

    @property
    def sub_message(self):
        """Get the sub-message."""
        return self._sub_message

    def to_json(self):
        """Output the message in JSON format."""
        return {"rule_id" : self.rule_id, "severity" : str(self.severity.name),
                "message" : self.message, "sub_message" : self.sub_message}

    def __str__(self):
        return 'id:{}, severity:{}, message:{}, sub_message:{}'.format(self.rule_id,
                                                                       str(self.severity.name),
                                                                       self.message,
                                                                       self.sub_message)

    @classmethod
    def from_values(cls, rule_id, severity=Severity.Error, sub_message=''):
        """Create an StructError from values supplied."""
        return StructError('CSIPSTR{}'.format(rule_id), severity,
                           STRUCT_ERRORS.get(rule_id), sub_message)

class ArchivePackageHandler():
    """Class to handle archive / compressed information packages."""
    def __init__(self, unpack_root=tempfile.gettempdir()):
        self._unpack_root = unpack_root

    @property
    def unpack_root(self):
        """Returns the root directory for archive unpacking."""
        return self._unpack_root

    def unpack_package(self, to_unpack, dest=None):
        """Unpack an archived package to a destination (defaults to tempdir).
        returns the destination folder."""
        if not os.path.isfile(to_unpack) or not self.is_archive(to_unpack):
            raise PackageStructError("File is not an archive file.")
        sha1 = UTILS.sha1(to_unpack)
        dest_root = dest if dest else self.unpack_root
        destination = os.path.join(dest_root, sha1)
        if zipfile.is_zipfile(to_unpack):
            zip_ip = zipfile.ZipFile(to_unpack)
            zip_ip.extractall(path=destination)
        elif tarfile.is_tarfile(to_unpack):
            tar_ip = tarfile.open(to_unpack)
            tar_ip.extractall(path=destination)
        return destination

    @staticmethod
    def is_archive(to_test):
        """Return True if the file is a recognised archive type, False otherwise."""
        if zipfile.is_zipfile(to_test):
            return True
        return tarfile.is_tarfile(to_test)

def validate_package_structure(package_path):
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

    def validate_manifest(self, is_root=True):
        """Validate a manifest report and return the list of validation errors."""
        validation_errors = []
        # [CSIPSTR4] Is there a file called METS.xml (perform case checks)
        # [CSIPSTR12] Does each representation folder have a METS.xml file? (W)
        if not self.has_mets:
            if is_root:
                validation_errors.append(StructError.from_values(4))
            else:
                validation_errors.append(StructError.from_values(12, severity=Severity.Warn))
        # [CSIPSTR5] Is there a first level folder called metadata?
        # [CSIPSTR13] Does each representation folder have a metadata folder (W)
        if not self.has_md:
            if is_root:
                validation_errors.append(StructError.from_values(5, severity=Severity.Warn))
            else:
                validation_errors.append(StructError.from_values(13, severity=Severity.Warn))
        # [CSIPSTR15] Is there a schemas folder at the root level/representations? (W)
        if not self.has_schema:
            validation_errors.append(StructError.from_values(15, severity=Severity.Warn))
        # [CSIPSTR11] Does each representation folder have a sub folder called data? (W)
        if not self.has_data and not is_root:
            validation_errors.append(StructError.from_values(11, severity=Severity.Warn))
        # [CSIPSTR9] Is there a first level folder called representations (W)
        if not self.has_reps and is_root:
            validation_errors.append(StructError.from_values(9, severity=Severity.Warn))
        return validation_errors

    @classmethod
    def from_directory(cls, dir_to_scan):
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
                if entry == "metadata":
                    has_md = True
                # [CSIPSTR15] Is there a schemas folder at the root level/representations? (W)
                elif entry == "schemas":
                    has_schema = True
                # [CSIPSTR11] Does each representation folder have a sub folder called data? (W)
                elif entry == "data":
                    has_data = True
                # [CSIPSTR9] Is there a first level folder called representations (W)
                elif entry == REPS_DIR:
                    has_reps = True
        return StructureChecker(name, has_mets, has_md, has_schema, has_data, has_reps)

class PackageStructError(RuntimeError):
    """Exception to signal fatal pacakge structure errors."""
    def __init__(self, arg):
        super(PackageStructError, self).__init__()
        self.args = arg
