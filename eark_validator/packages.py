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
"""
Factory methods for the package classes.
"""
import os
from pathlib import Path
import uuid

from eark_validator import structure
from eark_validator.infopacks.package_handler import PackageHandler, PackageError
from eark_validator.model.validation_report import ValidationReport
from eark_validator.model.package_details import PackageDetails

def validate(to_validate, check_metadata=True):
    """Returns the validation report that results from validating the path
    to_validate as a folder. The method does not validate archive files."""
    _, struct_results = structure.validate(to_validate)
    package = _get_info_pack(name=os.path.basename(to_validate))
    return ValidationReport(uid=uuid.uuid4(), structure=struct_results)

class PackageValidator():
    """Class for performing full package validation."""
    _package_handler = PackageHandler()
    def __init__(self, package_path, check_metadata=True):
        self._path = Path(package_path)
        self._name = os.path.basename(package_path)
        self._report = None
        if os.path.isdir(package_path) or PackageHandler.is_archive(package_path):
            # If a directory or archive get the path to process
            self._to_proc = self._path.absolute()
        elif self._name == 'METS.xml':
            mets_path = Path(package_path)
            self._to_proc = mets_path.parent.absolute()
            self._name = os.path.basename(self._to_proc)
        else:
            # If not an archive we can't process
            self._report = _report_from_bad_path(self.name, package_path)
            return
        self._report = validate(self._to_proc, check_metadata)

    @property
    def original_path(self):
        """Returns the original parsed path."""
        return self._path

    @property
    def name(self):
        """Returns the package name."""
        return self._name

    @property
    def validation_report(self):
        """Returns the valdiation report for the package."""
        return self._report

def _report_from_unpack_except(name, package_path):
    struct_results = structure.get_multi_root_results(package_path)
    return ValidationReport(structure=struct_results)

def _report_from_bad_path(name, package_path):
    struct_results = structure.get_bad_path_results(package_path)
    return ValidationReport(structure=struct_results)

def _get_info_pack(name, profile=None):
    return PackageDetails(name=name)
