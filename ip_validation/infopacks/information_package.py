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
from enum import Enum, unique
import os
import tarfile
import tempfile
import zipfile

from ip_validation.infopacks.struct_errors import StructError
from ip_validation.infopacks.rules import Severity

import ip_validation.utils as UTILS

@unique
class StructureStatus(Enum):
    """Enum covering information package validation statuses."""
    Unknown = 1
    # Package has basic parse / structure problems and can't be validated
    NotWellFormed = 2
    # Package structure is OK
    WellFormed = 3

class MetadataStatus(Enum):
    """Enum covering information package validation statuses."""
    Unknown = 1
    # Package Metatdata is valid
    Invalid = 2
    # Package structure and metadata are both OK
    Valid = 3

@unique
class ManifestStatus(Enum):
    """Enum covering information package manifest statuses."""
    Unknown = 1
    # Files are missing from the manifest/metadata reference, or there are files
    # on the file system not mentioned in any manifest or metadata record.
    Incomplete = 2
    # Files are all present but there is a problem verifying size or checksum Information
    # in package
    Inconsistent = 3
    # All files are present, with matching size and checksum data.
    Consistent = 4

class PackageDetails:
    """Stores the vital facts and figures about a package."""
    structure_values = list(StructureStatus)
    manifest_values = list(ManifestStatus)
    def __init__(self, path, size=0, version='unknown',
                 structure_status=StructureStatus.Unknown,
                 manifest_status=ManifestStatus.Unknown):
        self._path = path
        self._size = size
        self._version = version
        self.structure_status = structure_status
        self.manifest_status = manifest_status
        self._errors = []

    @property
    def path(self):
        """Get the package root directory path."""
        return self._path

    @property
    def name(self):
        """Get the name of the package."""
        return os.path.basename(os.path.normpath(self.path))

    @property
    def size(self):
        """Return the package size in bytes."""
        return self._size

    @property
    def version(self):
        """Get the version of the package."""
        return self._version

    @property
    def structure_status(self):
        """Get the package status."""
        return self._structure_status

    @structure_status.setter
    def structure_status(self, value):
        if not value in self.structure_values:
            raise ValueError("Illegal package status value")
        self._structure_status = value

    @property
    def manifest_status(self):
        """Get the package status."""
        return self._manifest_status

    @manifest_status.setter
    def manifest_status(self, value):
        if not value in self.manifest_values:
            raise ValueError("Illegal manifest status value")
        self._manifest_status = value

    def add_error(self, error):
        """Add a validation error to package lists."""
        self._errors.append(error)
        if error.severity == Severity.Error:
            self.structure_status = StructureStatus.NotWellFormed

    def add_errors(self, errors):
        """Add a validation error to package lists."""
        for error in errors:
            self.add_error(error)

    @property
    def errors(self):
        """Return the full list of errors."""
        return self._errors

class ArchivePackageHandler():
    """Class to handle archive / compressed information packages."""
    def __init__(self, unpack_root=tempfile.gettempdir()):
        self._unpack_root = unpack_root

    @property
    def unpack_root(self):
        """Returns the root directory for archive unpacking."""
        return self._unpack_root

    @staticmethod
    def is_archive(to_test):
        """Return True if the file is a recognised archive type, False otherwise."""
        if zipfile.is_zipfile(to_test):
            return True
        return tarfile.is_tarfile(to_test)

    def unpack_package(self, to_unpack, dest=None):
        """Unpack an archived package to a destination (defaults to tempdir)."""
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

METS_NAME = 'METS.xml'
REPS_DIR = "representations"
def validate_package_structure(package_path):
    """Carry out all structural package tests."""
    # It's a file so we need to unpack it
    details = PackageDetails(package_path) \
        if os.path.isdir(package_path) \
        else unpack_package(package_path)
    # Check it's not a broken package as unpack errors are terminal
    if details.structure_status == StructureStatus.NotWellFormed:
        return details
    # Now carry out the root checks on the package
    details = check_package_root(details.path)
    # If it has basic structure errors then bale.
    if details.structure_status == StructureStatus.NotWellFormed:
        return details

    # [CSIPSTR2] Do package name and <mets objid="?" > match?
    #   - Defferred to corresponding metadata check?

    # Now get the manifests directory
    root_manifest = PackageManifest.from_directory(details.path)
    # if we have manifests then we need the details from them also
    rep_manifests = representation_manifests(os.path.join(details.path, REPS_DIR))
    root_errors = validate_manifest(root_manifest)
    rep_errors = []
    for manifest in rep_manifests.values():
        rep_errors = rep_errors + validate_manifest(manifest, is_root=False)
    validation_errors = root_errors + rep_errors
    details.add_errors(validation_errors)
    if details.structure_status == StructureStatus.Unknown:
        details.structure_status = StructureStatus.WellFormed
    return details

def validate_manifest(manifest, is_root=True):
    """Validate a manifest report and return the list of validation errors."""
    validation_errors = []
    # [CSIPSTR4] Is there a file called METS.xml (perform case checks)
    # [CSIPSTR12] Does each representation folder have a METS.xml file? (W)
    if not manifest.has_mets:
        if is_root:
            validation_errors.append(StructError.from_values(4))
        else:
            validation_errors.append(StructError.from_values(12, severity=Severity.Warn))
    # [CSIPSTR5] Is there a first level folder called metadata?
    # [CSIPSTR13] Does each representation folder have a metadata folder (W)
    if not manifest.has_md:
        if is_root:
            validation_errors.append(StructError.from_values(5, severity=Severity.Warn))
        else:
            validation_errors.append(StructError.from_values(13, severity=Severity.Warn))
    # [CSIPSTR15] Is there a schemas folder at the root level/representations? (W)
    if not manifest.has_schema:
        validation_errors.append(StructError.from_values(15, severity=Severity.Warn))
    # [CSIPSTR11] Does each representation folder have a sub folder called data? (W)
    if not manifest.has_data and not is_root:
        validation_errors.append(StructError.from_values(11, severity=Severity.Warn))
    # [CSIPSTR9] Is there a first level folder called representations (W)
    if not manifest.has_reps and is_root:
        validation_errors.append(StructError.from_values(9, severity=Severity.Warn))
    return validation_errors

def representation_manifests(reps_dir):
    """Loop through reps and get the details."""
    rep_manifests = {}
    if not os.path.isdir(reps_dir):
        return rep_manifests
    for entry in os.listdir(reps_dir):
        rep_dir = os.path.join(reps_dir, entry)
        if os.path.isdir(rep_dir):
            rep_manifest = PackageManifest.from_directory(rep_dir)
            rep_manifests[rep_manifest.name] = rep_manifest
    return rep_manifests

def unpack_package(package_path):
    """Unpack what's presumed to be an archive format package. Report any issues
    with the archive."""
    # It's a file so we need to unpack it
    archive_handler = ArchivePackageHandler()
    unpacked_dir = package_path
    try:
        unpacked_dir = archive_handler.unpack_package(package_path)
    except PackageStructError:
        # If it's a file and it can't be unpacked that's about all we can do.
        details = PackageDetails(package_path, structure_status=StructureStatus.NotWellFormed)
        details.add_error(StructError.from_values(1, sub_message="""Package file
                          is not a recognised archive format."""))
        return details
    return PackageDetails(os.path.normpath(unpacked_dir))

def check_package_root(package_root):
    """Ensure that the root package directory is of the correct form."""
    # [CSIPSTR1] Is reference a single physical folder?
    # get root entries (files and folders)
    root_entries = os.listdir(package_root)
    if len(root_entries) != 1:
        details = PackageDetails(package_root, structure_status=StructureStatus.NotWellFormed)
        details.add_error(StructError.from_values(1, sub_message="""Multiple root
                          elements found when unpacking {}""".format(package_root)))
        return details
    if os.path.isfile(os.path.join(package_root, root_entries[0])):
        details = PackageDetails(package_root, structure_status=StructureStatus.NotWellFormed)
        details.add_error(StructError.from_values(1, sub_message="""Package {}
                          unpacked to a single file.""".format(package_root)))
        return details
    return PackageDetails(os.path.normpath(os.path.join(package_root,
                                                        root_entries[0])))

class PackageManifest():
    """Encapsulate the mess that is the manifest details."""
    def __init__(self, name, has_mets=True, has_md=True, has_schema=True,
                 has_data=False, has_reps=True):
        self.name = name
        self.has_mets = has_mets
        self.has_md = has_md
        self.has_schema = has_schema
        self.has_data = has_data
        self.has_reps = has_reps

    @classmethod
    def from_directory(cls, dir_to_scan):
        """Create a manifest instance from a directory."""
        has_mets = False
        has_ghost_mets = False
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
                else:
                    has_ghost_mets = True
            elif entry.lower() == METS_NAME.lower():
                has_ghost_mets = True
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
        return PackageManifest(name, has_mets, has_md, has_schema, has_data, has_reps)

class PackageStructError(RuntimeError):
    """Exception to signal fatal pacakge structure errors."""
    def __init__(self, arg):
        super(PackageStructError, self).__init__()
        self.args = arg
