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

@unique
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

class InformationPackage:
    """Stores the vital facts and figures about a package."""
    def __init__(self, details, specification, validation_report):
        self._details = details
        self._specification = specification
        self._validation_report = validation_report

    @property
    def details(self):
        """Get the package details."""
        return self._details

    @property
    def specification(self):
        """Get the specification of the package."""
        return self._specification

    @property
    def validation_report(self):
        """Return the package validation_report."""
        return self._validation_report

    def __str__(self):
        return "name:" + self.details.name + ", details:" + \
            str(self.details) + ", specification:" + str(self.specification)

class PackageDetails:
    """Stores the vital facts and figures about a package."""
    def __init__(self, path, size, specification):
        self._path = path
        self._size = size
        self._specification = specification

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
    def specification(self):
        """Get the specification of the package."""
        return self._specification

    def __str__(self):
        return "name:" + self.name + " path:" + self.path + ", size:" + \
            str(self.size) + ", specification:" + str(self.specification)
