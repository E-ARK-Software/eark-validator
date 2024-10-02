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

from eark_validator import rules as SC
from eark_validator import structure
from eark_validator.infopacks.information_package import InformationPackages
from eark_validator.infopacks.package_handler import PackageHandler
from eark_validator.mets import MetsValidator
from eark_validator.model import ValidationReport
from eark_validator.model.package_details import InformationPackage
from eark_validator.model.validation_report import MetadataResults, MetadataStatus, MetatdataResultSet, Result, Severity
from eark_validator.specifications.specification import SpecificationType, SpecificationVersion

METS: str = 'METS.xml'

class PackageValidator():
    """Class for performing full package validation."""
    _package_handler = PackageHandler()
    def __init__(self, package_path: Path, version: SpecificationVersion = SpecificationVersion.V2_1_0):
        self._path : Path = package_path
        self._name: str = os.path.basename(package_path)
        self._report: ValidationReport = None
        self._version: SpecificationVersion = version

        if os.path.isdir(package_path):
            # If a directory or archive get the path to process
            self._to_proc = self._path.absolute()
        elif PackageHandler.is_archive(package_path):
            self._to_proc = self._package_handler.prepare_package(package_path)
        elif self._name == METS:
            mets_path = Path(package_path)
            self._to_proc = mets_path.parent.absolute()
            self._name = os.path.basename(self._to_proc)
        else:
            # If not an archive we can't process
            self._report = _report_from_bad_path(package_path)
            return

        self._report = self.validate(self._version, self._to_proc, PackageHandler.is_archive(package_path))

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

    @property
    def version(self) -> SpecificationVersion:
        """Returns the specifiation version used for validation."""
        return self._version

    @classmethod
    def validate(cls, version: SpecificationVersion, to_validate: Path, is_archive: bool=False) -> ValidationReport:
        """Returns the validation report that results from validating the path
        to_validate as a folder. The method does not validate archive files."""
        is_struct_valid, struct_results = structure.validate(to_validate, is_archive)
        if not is_struct_valid:
            return ValidationReport.model_validate({'structure': struct_results})
        validator = MetsValidator(str(to_validate))
        validator.validate_mets(METS)

        csip_profile = SC.ValidationProfile(SpecificationType.CSIP, version)
        csip_profile.validate(to_validate.joinpath(METS))
        results = csip_profile.get_all_results()

        package: InformationPackage = InformationPackages.from_path(to_validate)
        if package.details.oaispackagetype in ['SIP', 'DIP']:
            profile = SC.ValidationProfile(SpecificationType.from_string(package.details.oaispackagetype), version)
            profile.validate(to_validate.joinpath(METS))
            results.extend(profile.get_all_results())

        metadata: MetatdataResultSet = MetatdataResultSet.model_validate({
            'schema_results': MetadataResults.model_validate({ 'status': _validity_from_messages(validator.validation_errors), 'messages': validator.validation_errors }),
            'schematron_results': MetadataResults.model_validate({ 'status': _validity_from_messages(results), 'messages': results })
            })
        return ValidationReport.model_validate({
            'structure': struct_results,
            'package': package,
            'metadata': metadata
            })

def _validity_from_messages(messages: list[Result]) -> MetadataStatus:
    return MetadataStatus.VALID if len([ res for res in messages if res.severity == Severity.ERROR]) == 0 else MetadataStatus.INVALID

def _report_from_bad_path(package_path: Path) -> ValidationReport:
    struct_results = structure.get_bad_path_results(package_path)
    return ValidationReport.model_validate({ 'structure': struct_results })
