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
import os

class InformationPackage:
    """Stores the vital facts and figures about a package."""
    def __init__(self, path, details, files=None):
        self._path = path
        self._details = details
        self._files = files if files else []

    @property
    def path(self):
        """Get the specification of the package."""
        return self._path

    @property
    def details(self):
        """Get the package details."""
        return self._details

    @property
    def files(self):
        """Get a list of details for all files found in the package."""
        return self._details

    def __str__(self):
        return 'name: ' + self.details.name + ', details: ' + \
            str(self.details) + ', specification: ' + str(self.specification) + ', files: ' + len(self._files)

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
        
    def __str__(self):
        return 'name: ' + self.name + ', specification: ' + self._specification + ', size: ' + \
            str(self.size)
