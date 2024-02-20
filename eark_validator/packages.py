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

from eark_validator import rules as SC
from eark_validator import structure
from eark_validator.infopacks.information_package import InformationPackages
from eark_validator.infopacks.package_handler import PackageHandler
from eark_validator.mets import MetsValidator
from eark_validator.model import ValidationReport
from eark_validator.model import PackageDetails
from eark_validator.model.package_details import InformationPackage
from eark_validator.model.validation_report import MetatdataResults

def validate(to_validate: Path, check_metadata: bool=True) -> ValidationReport:
    """Returns the validation report that results from validating the path
    to_validate as a folder. The method does not validate archive files."""
    is_struct_valid, struct_results = structure.validate(to_validate)
    if not is_struct_valid:
        return ValidationReport.model_validate({'structure': struct_results})
    validator = MetsValidator(str(to_validate))
    validator.validate_mets('METS.xml')
    if (not validator.is_valid):
        metadata: MetatdataResults = MetatdataResults.model_validate({ 'schema_results': validator.validation_errors })
        return ValidationReport.model_validate({'structure': struct_results, 'metadata': metadata})
    package: InformationPackage = InformationPackages.from_path(to_validate)
    package_type = package.package.oaispackagetype if package.package.oaispackagetype else 'CSIP'
    package_type = 'CSIP' if package_type == 'AIP' else package_type
    profile = SC.ValidationProfile.from_specification(package_type)
    profile.validate(to_validate.joinpath('METS.xml'))
    results = profile.get_all_results()
    metadata: MetatdataResults = MetatdataResults.model_validate({'schema_results': validator.validation_errors, 'schematron_results': results})
    return ValidationReport.model_validate({'structure': struct_results, 'package': package, 'metadata': metadata})

class PackageValidator():
    """Class for performing full package validation."""
    _package_handler = PackageHandler()
    def __init__(self, package_path: Path, check_metadata=True):
        self._path : Path = package_path
        self._name: str = os.path.basename(package_path)
        self._report: ValidationReport = None
        if os.path.isdir(package_path):
            # If a directory or archive get the path to process
            self._to_proc = self._path.absolute()
        elif PackageHandler.is_archive(package_path):
            self._to_proc = self._package_handler.prepare_package(package_path)
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
    def original_path(self) -> Path:
        """Returns the original parsed path."""
        return self._path

    @property
    def name(self) -> str:
        """Returns the package name."""
        return self._name

    @property
    def validation_report(self) -> ValidationReport:
        """Returns the valdiation report for the package."""
        return self._report

def _report_from_unpack_except(name: str, package_path: Path) -> ValidationReport:
    struct_results = structure.get_multi_root_results(package_path)
    return ValidationReport.model_validate({ 'structure': struct_results })

def _report_from_bad_path(name: str, package_path: Path) -> ValidationReport:
    struct_results = structure.get_bad_path_results(package_path)
    return ValidationReport.model_validate({ 'structure': struct_results })

def _get_info_pack(name: str, profile=None) -> PackageDetails:
    return PackageDetails.model_validate({ 'name': name })
