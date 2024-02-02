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
"""Information Package manifests."""
import os
from pathlib import Path

import lxml.etree as ET
from eark_validator.mets import MetsFiles
from eark_validator.model.metadata import FileEntry

from eark_validator.utils import get_path
from eark_validator.const import NO_PATH, NOT_DIR, NOT_FILE
from eark_validator.model import (
    Checksum,
    ChecksumAlg,
    Manifest,
    ManifestEntry
    )
from eark_validator.model.manifest import SourceType

class Checksummer:
    def __init__(self, algorithm: ChecksumAlg | str):
        self._algorithm: ChecksumAlg = algorithm if isinstance(algorithm, ChecksumAlg) else ChecksumAlg.from_string(algorithm)

    @property
    def algorithm(self) -> ChecksumAlg:
        """Get the algorithm."""
        return self._algorithm

    def hash_file(self, path: Path) -> 'Checksum':
        if (not path.exists()):
            raise FileNotFoundError(NO_PATH.format(path))
        if (not path.is_file()):
            raise ValueError(NOT_FILE.format(path))
        implemenation = ChecksumAlg.get_implementation(self._algorithm)
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                implemenation.update(chunk)
        return Checksum.model_validate({'algorithm': self._algorithm, 'value': implemenation.hexdigest()}, strict=True)

    @classmethod
    def from_file(cls, path: Path, algorithm: 'ChecksumAlg') -> 'Checksum':
        """Create a Checksum from an etree element."""
        # Get the child flocat element and grab the href attribute.
        return Checksummer(algorithm).hash_file(path)

class ManifestEntries:
    @staticmethod
    def from_file_path(path: Path, checksum_algorithm: ChecksumAlg | str=None) -> ManifestEntry:
        """Create a FileItem from a file path."""
        if (not os.path.exists(path)):
            raise FileNotFoundError(NO_PATH.format(path))
        if (not os.path.isfile(path)):
            raise ValueError('Path {} is not a file.'.format(path))
        algorithm = checksum_algorithm if isinstance(checksum_algorithm, ChecksumAlg) else ChecksumAlg.from_string(checksum_algorithm)
        checksums = [ Checksummer.from_file(path, algorithm) ] if checksum_algorithm else []
        return ManifestEntry.model_validate({
            'path': path,
            'size': os.path.getsize(path),
            'checksums': checksums
            })

    @staticmethod
    def from_file_entry(entry: FileEntry) -> ManifestEntry:
        """Create a FileItem from a FileEntry."""
        return ManifestEntry.model_validate({
            'path': entry.path,
            'size': entry.size,
            'checksums': [ entry.checksum ]
            })

class Manifests:
    @classmethod
    def validate_manifest(cls, path: Path, manifest: Manifest) -> tuple[bool, list[str]]:
        """Check the integrity of the manifest."""
        is_valid = True
        issues = []
        for entry in manifest.entries:
            abs_path = Path(os.path.join(path, entry.path))
            if not abs_path.is_file():
                is_valid = False
                issues.append('File {} is missing.'.format(entry.path))
                continue
            if (entry.size != os.path.getsize(abs_path)):
                issues.append('File {} manifest size {}, filesystem size {}.'.format(entry.path, entry.size, os.path.getsize(abs_path)))
                is_valid = False
            calced_checksum = Checksummer.from_file(abs_path, entry.checksum.algorithm)
            if not entry.checksum == calced_checksum:
                issues.append('File {} manifest checksum {}, calculated checksum {}.'.format(entry.path, entry.checksum, calced_checksum))
                is_valid = False
        return is_valid, issues

    @staticmethod
    def _relative_path(root_path: str, path: str) -> str:
        return path if not os.path.isabs(path) else os.path.relpath(path, root_path)

    @staticmethod
    def from_source(source: Path | str, checksum_algorithm: ChecksumAlg=None) -> Manifest:
        path = get_path(source, True)
        if (path.is_file()):
            return Manifests.from_mets_file(path)
        elif (path.is_dir()):
            return Manifests.from_directory(path, checksum_algorithm=checksum_algorithm)
        else:
            raise ValueError('Path {} is neither a file nor a directory.'.format(source))

    @staticmethod
    def from_directory(source: Path | str, checksum_algorithm: ChecksumAlg=None) -> Manifest:
        path = get_path(source, True)
        if (not path.is_dir()):
            raise ValueError(NOT_DIR.format(source))
        entries = []
        for subdir, dirs, files in os.walk(source):
            for file in files:
                file_path = Path(os.path.join(subdir, file))
                entries.append(ManifestEntries.from_file_path(file_path, checksum_algorithm=checksum_algorithm))
        return Manifest.model_validate({
            'source': SourceType.PACKAGE,
            'summary': None,
            'entries': entries
            })

    @staticmethod
    def from_mets_file(source: Path | str) -> Manifest:
        path: Path = get_path(source, True)
        if (not path.is_file()):
            raise ValueError(NOT_FILE.format(source))
        mets_file = MetsFiles.from_file(path)
        entries: list[ManifestEntry] = list(map(ManifestEntries.from_file_entry, mets_file.file_references))
        return Manifest.model_validate({
            'source': SourceType.METS,
            'summary': None,
            'entries': entries
            })
