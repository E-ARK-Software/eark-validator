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
    UNK = 'Unknown'
    # Package Metatdata is valid
    INVLD = 'Invalid'
    # Package structure and metadata are both OK
    VLD = 'Valid'

@unique
class ManifestStatus(Enum):
    """Enum covering information package manifest statuses."""
    UNK = 'Unknown'
    # Files are missing from the manifest/metadata reference, or there are files
    # on the file system not mentioned in any manifest or metadata record.
    INCMPLT = 'Incomplete'
    # Files are all present but there is a problem verifying size or checksum Information
    # in package
    INCNSTNT = 'Inconsistent'
    # All files are present, with matching size and checksum data.
    CNSTNT = 'Consistent'

class InformationPackage:
    """Stores the vital facts and figures about a package."""
    def __init__(self, path, details):
        self._path = path
        self._details = details

    @property
    def path(self):
        """Get the specification of the package."""
        return self._path

    @property
    def details(self):
        """Get the package details."""
        return self._details

    def __str__(self):
        return "name:" + self.details.name + ", details:" + \
            str(self.details) + ", specification:" + str(self.specification)

class PackageDetails:
    """Stores the vital facts and figures about a package."""
    def __init__(self, specification, size):
        self._specification = specification
        self._size = size

    @property
    def specification(self):
        """Get the specification."""
        return self._specification

    @property
    def name(self):
        """Get the name of the package."""
        return os.path.basename(os.path.normpath(self.path))

    @property
    def size(self):
        """Return the package size in bytes."""
        return self._size

    @classmethod
    def from_mets(cls, mets_path):
        pass
        
    def __str__(self):
        return "name: " + self.name + ", specification: " + self._specification + ", size: " + \
            str(self.size)
