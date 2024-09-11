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
"""Module covering information package structure validation and navigation."""
from pathlib import Path
from lxml import etree

from eark_validator.const import NO_PATH, NOT_FILE, NOT_VALID_FILE
from eark_validator.mets import MetsFiles, MetsFile
from eark_validator.ipxml.namespaces import Namespaces
from eark_validator.model import PackageDetails
from eark_validator.model.package_details import InformationPackage
from eark_validator.model.validation_report import Result
from .package_handler import PackageHandler

CONTENTINFORMATIONTYPE = 'contentinformationtype'
QUAL_CONTENTINFORMATIONTYPE = Namespaces.CSIP.qualify(CONTENTINFORMATIONTYPE.upper())
QUAL_OTHERTYPE = Namespaces.CSIP.qualify('OTHERTYPE')
QUAL_OAISPACKAGETYPE = Namespaces.CSIP.qualify('OAISPACKAGETYPE')
METS = 'mets'
METS_FILE = 'METS.xml'
QUAL_METS = Namespaces.METS.qualify(METS)
QUAL_METSHDR = Namespaces.METS.qualify('metsHdr')

class InformationPackages:

    @staticmethod
    def details_from_mets_file(mets_file: Path) -> PackageDetails:
        if not mets_file.exists():
            raise FileNotFoundError(NO_PATH.format(mets_file))
        if not mets_file.is_file():
            raise ValueError(NOT_FILE.format(mets_file))
        ns = {}
        label = othertype = contentinformationtype = oaispackagetype = ''
        try:
            parsed_mets = etree.iterparse(mets_file, events=['start', 'start-ns'])
            for event, element in parsed_mets:
                if event == 'start-ns':
                    # Add namespace id to the dictionary
                    ns[element[1]] = element[0]
                if event == 'start':
                    if element.tag == QUAL_METS:
                        label = element.get('LABEL', '')
                        othertype = element.get(QUAL_OTHERTYPE, '')
                        contentinformationtype = element.get(QUAL_CONTENTINFORMATIONTYPE, '')
                        oaispackagetype = element.find(QUAL_METSHDR).get(QUAL_OAISPACKAGETYPE, '')
                    else:
                        break
        except (etree.XMLSyntaxError, AttributeError) as ex:
            raise ValueError(NOT_VALID_FILE.format(mets_file, 'XML')) from ex
        return PackageDetails.model_validate({
            'name': mets_file.parent.stem,
            'label': label,
            'othertype': othertype,
            CONTENTINFORMATIONTYPE: contentinformationtype,
            'oaispackagetype': oaispackagetype
        })

    @staticmethod
    def from_path(package_path: Path) -> InformationPackage:
        if not package_path.exists():
            raise FileNotFoundError(NO_PATH.format(package_path))
        handler: PackageHandler = PackageHandler()
        to_parse:Path = handler.prepare_package(package_path)
        mets_path: Path = to_parse.joinpath(METS_FILE)
        if not mets_path.is_file():
            raise ValueError('No METS file found in package')
        mets: MetsFile = MetsFiles.from_file(to_parse.joinpath(METS_FILE))
        return InformationPackage.model_validate({
            METS: mets,
            'details': InformationPackages.details_from_mets_file(to_parse.joinpath(METS_FILE))
        })

    @staticmethod
    def validate(package_path: Path) -> Result:
        if not package_path.exists():
            raise FileNotFoundError(NO_PATH.format(package_path))
        handler: PackageHandler = PackageHandler()
        to_parse:Path = handler.prepare_package(package_path)
        mets_path: Path = to_parse.joinpath(METS_FILE)
        if not mets_path.is_file():
            raise ValueError('No METS file found in package')
        return True
