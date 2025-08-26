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
from typing import Optional, List

from eark_validator import rules as SC
from eark_validator import structure
from eark_validator.infopacks.information_package import InformationPackages
from eark_validator.infopacks.package_handler import PackageHandler
from eark_validator.mets import MetsValidator, MetsFiles, FileEntry
from eark_validator.model import ValidationReport, PackageDetails
from eark_validator.model.package_details import InformationPackage, MetsFile, Representation
from eark_validator.model.validation_report import MetadataResults, MetadataStatus, MetadataResultSet, Result, Severity
from eark_validator.specifications.specification import SpecificationType, SpecificationVersion

METS: str = 'METS.xml'

class PackageValidator():
    """Class for performing full package validation."""
    _package_handler = PackageHandler()
    def __init__(self, package_path: Path, type: Optional[SpecificationType], version: SpecificationVersion = SpecificationVersion.V2_1_0):
        self._path : Path = package_path
        self._name: str = os.path.basename(package_path)
        self._report: ValidationReport = None
        self._version: SpecificationVersion = version
        self._compressed = False

        if os.path.isdir(package_path):
            # If a directory or archive get the path to process
            self._to_proc = self._path.absolute()
        elif PackageHandler.is_archive(package_path):
            self._to_proc = self._package_handler.prepare_package(package_path)
            self._compressed = True
        elif self._name == METS:
            mets_path = Path(package_path)
            self._to_proc = mets_path.parent.absolute()
            self._name = os.path.basename(self._to_proc)
        else:
            # If not an archive we can't process
            self._report = _report_from_bad_path(package_path)
            return

        self._report = self.validate(self._to_proc, self._version, type)

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

    @property
    def compressed(self) -> bool:
        """Returns whether the package was contained in compressed form."""
        return self._compressed

    def validate(self, path_to_package: Path, version: SpecificationVersion, forced_type: Optional[SpecificationType]) -> ValidationReport:
        #structure
        structure_checker = structure.StructureChecker(path_to_package, self.compressed)
        if structure_checker.results.status != structure.StructureStatus.WELLFORMED:
            return ValidationReport.model_validate({'structure': structure_checker.results})
        
        #metadata
        root_mets_path: Path = path_to_package.joinpath(METS)
        package_details: PackageDetails = InformationPackages.details_from_mets_file(root_mets_path)
        type: Optional[SpecificationType] = None
        if forced_type:
            type = forced_type
        else:
            if package_details.oaispackagetype in ['SIP', 'DIP']:
                type = SpecificationType.from_string(package_details.oaispackagetype)

        metadata_results: MetadataResultSet = self.__validate_mets(path_to_package, version, type)
        
        for representation in structure_checker.representations.keys():
            if representation.joinpath(METS).is_file():
                representation_metadata_results: MetadataResultSet = self.__validate_mets(representation, version, type)
                metadata_results = metadata_results.merge(representation_metadata_results)
        
        #package
        package_mets: MetsFile = MetsFiles.from_file(root_mets_path)
        package_representations: List[Representation] = []
        for representation in structure_checker.representations.keys():
            representation_path = Path(representation)
            representation_mets_path = representation_path.joinpath(METS)
            if representation_mets_path.is_file():
                package_representation_mets = MetsFiles.from_file(representation_mets_path)

                package_representations.append(Representation.model_validate({
                    'mets': package_representation_mets,
                    'name':  representation_mets_path.parent.name
                }))

        package_mets.file_entries.extend(self.__find_undefined_files(MetsFiles.file_paths_defined_in_mets_files, path_to_package))
        
        package: InformationPackage = InformationPackage.model_validate({
            'mets': package_mets,
            'details': package_details,
            'representations': package_representations
        })

        return ValidationReport.model_validate({
            'structure': structure_checker.results,
            'metadata': metadata_results,
            'package': package,
            })
        
    def __validate_mets(self, path_to_package: Path, version: SpecificationVersion, type: Optional[SpecificationType]) -> MetadataResultSet:
        mets_path: Path = path_to_package.joinpath(METS)
        validator = MetsValidator(mets_path)
        is_mets_valid = validator.validate_against_schema()
        if not is_mets_valid:
            return MetadataResultSet.model_validate({
                'schema_results': MetadataResults.model_validate(
                    { 
                        'status': _validity_from_messages(validator.validation_errors), 
                        'messages': validator.validation_errors 
                    })})
        
        csip_profile = SC.ValidationProfile(SpecificationType.CSIP, version, path_to_package)
        csip_profile.validate(mets_path)
        results = csip_profile.get_all_results()

        if type and type != SpecificationType.CSIP:
            specific_profile: SC.ValidationProfile = SC.ValidationProfile(type, version, path_to_package)
            specific_profile.validate(mets_path)
            results.extend(specific_profile.get_all_results())

        return MetadataResultSet.model_validate({
            'schema_results': MetadataResults.model_validate({ 'status': _validity_from_messages(validator.validation_errors), 'messages': validator.validation_errors }),
            'schematron_results': MetadataResults.model_validate({ 'status': _validity_from_messages(results), 'messages': results })
            })
    
    def __find_undefined_files(self, defined_files_in_mets_files: set[Path], package_path: Path) -> List[FileEntry]:
        package_path = package_path.resolve()
        all_files_in_package: set[Path] = {f.resolve() for f in Path(package_path).rglob("*") if f.is_file()}
        defined_files = {p.resolve() for p in defined_files_in_mets_files}

        undefined_files = all_files_in_package.difference(defined_files)
        return [FileEntry.model_validate({
                    'path': str(p.relative_to(package_path)),
                    'isValid': False,
                    'errors': ['File is not referenced in any mets file.'],
                    'size': None,
                    'checksum': None,
                    'mimetype': None
                }) for p in undefined_files]
        
def _validity_from_messages(messages: list[Result]) -> MetadataStatus:
    return MetadataStatus.VALID if len([ res for res in messages if res.severity == Severity.ERROR]) == 0 else MetadataStatus.INVALID

def _report_from_bad_path(package_path: Path) -> ValidationReport:
    struct_results = structure.get_bad_path_results(package_path)
    return ValidationReport.model_validate({ 'structure': struct_results })
