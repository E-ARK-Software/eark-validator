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
import tarfile
import tempfile
import zipfile
from eark_validator.infopacks.manifest import Checksummer
SUB_MESS_NOT_EXIST = 'Path {} does not exist'
SUB_MESS_NOT_ARCH = 'Parameter "to_unpack": {} does not reference a file of known archive format (zip or tar).'

class PackageError(Exception):
    """Exception used to mark validation error when unpacking archive."""

class PackageHandler():
    """Class to handle archive / compressed information packages."""
    def __init__(self, unpack_root: Path=Path(tempfile.gettempdir())):
        self._unpack_root : Path = unpack_root

    @property
    def unpack_root(self) -> Path:
        """Returns the root directory for archive unpacking."""
        return self._unpack_root

    def prepare_package(self, to_prepare: Path, dest: Path=None) -> Path:
        if not os.path.exists(to_prepare):
            raise ValueError(SUB_MESS_NOT_EXIST.format(to_prepare))
        if os.path.isdir(to_prepare):
            return to_prepare
        return self.unpack_package(to_prepare, dest)

    def unpack_package(self, to_unpack: Path, dest: Path=None) -> Path:
        """Unpack an archived package to a destination (defaults to tempdir).
        returns the destination folder."""
        if not os.path.isfile(to_unpack) or not self.is_archive(to_unpack):
            raise ValueError(SUB_MESS_NOT_ARCH.format(to_unpack))
        sha1 = Checksummer('SHA-1').hash_file(to_unpack)
        dest_root = dest if dest else self.unpack_root
        destination = os.path.join(dest_root, sha1.value)
        self._unpack(to_unpack, destination)

        children = []
        for path in Path(destination).iterdir():
            children.append(path)
        if len(children) != 1:
            # Dir unpacks to more than a single folder
            raise PackageError('Unpacking archive yields'
                                  '{} children.'.format(len(children)))
        if not os.path.isdir(children[0]):
            raise PackageError('Unpacking archive yields'
                                  'a single file child {}.'.format(children[0]))
        return children[0].absolute()

    @staticmethod
    def _unpack(to_unpack: Path, destination: Path) -> None:
        if zipfile.is_zipfile(to_unpack):
            with zipfile.ZipFile(to_unpack) as zip_ip:
                zip_ip.extractall(path=destination)
        elif tarfile.is_tarfile(to_unpack):
            with tarfile.open(to_unpack) as tar_ip:
                tar_ip.extractall(path=destination)

    @staticmethod
    def is_archive(to_test: Path) -> bool:
        """Return True if the file is a recognised archive type, False otherwise."""
        if os.path.isfile(to_test):
            if zipfile.is_zipfile(to_test):
                return True
            return tarfile.is_tarfile(to_test)
        return False
