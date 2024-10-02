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
import pickle
from pathlib import Path
from typing import Optional

from eark_validator.const import NO_PATH, NOT_DIR, NOT_FILE
from eark_validator.mets import MetsFiles
from eark_validator.model import Checksum, ChecksumAlg, Manifest, ManifestEntry
from eark_validator.model.manifest import SourceType
from eark_validator.model.metadata import FileEntry
from eark_validator.utils import get_path
from eark_validator.infopacks.checksummer import Checksummer

class ManifestEntries:
    @staticmethod
    def from_file_path(root: Path, entry_path: Path,
                       checksum_algorithm: ChecksumAlg | str=None) -> ManifestEntry:
        """Create a FileItem from a file path."""
        abs_path: Path = root.joinpath(entry_path).absolute()
        if not os.path.exists(abs_path):
            raise FileNotFoundError(NO_PATH.format(abs_path))
        if not os.path.isfile(abs_path):
            raise ValueError(f'Path {abs_path} is not a file.')
        if isinstance(checksum_algorithm, ChecksumAlg):
            algorithm: ChecksumAlg = checksum_algorithm
        else:
            algorithm: ChecksumAlg = ChecksumAlg.from_string(checksum_algorithm)
        checksums = [ Checksummer.from_file(abs_path, algorithm) ] if checksum_algorithm else []
        return ManifestEntry.model_validate({
            'path': str(entry_path),
            'size': os.path.getsize(abs_path),
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
    def validate_manifest(cls, manifest: Manifest,
                          alt_root: Optional[Path] = None) -> tuple[bool, list[str]]:
        """Check the integrity of the manifest."""
        issues: list[str] = []
        root = alt_root if alt_root else _resolve_manifest_root(manifest)
        for entry in manifest.entries:
            abs_path = Path(os.path.join(root, entry.path))
            if not abs_path.is_file():
                issues.append(f'File {abs_path} is missing.')
                continue
            if entry.size != os.path.getsize(abs_path):
                size = os.path.getsize(abs_path)
                issues.append(f'File {entry.path} manifest size {entry.size}, file size {size}.')
            check_issues: list[str] = _test_checksums(abs_path, entry.checksums)
            if not bool(check_issues):
                issues.extend(check_issues)
        return (not bool(issues)), issues

    @staticmethod
    def from_source(source: Path | str, checksum_algorithm: ChecksumAlg=None) -> Manifest:
        path = get_path(source, True)
        if path.is_file():
            return Manifests.from_mets_file(path)
        if path.is_dir():
            return Manifests.from_directory(path, checksum_algorithm=checksum_algorithm)
        raise ValueError(f'Path {source} is neither a file nor a directory.')

    @staticmethod
    def to_file(manifest: Manifest, path: Path | str) -> None:
        path = get_path(path, False)
        with open(path, 'wb') as file:
            pickle.dump(manifest, file)

    @staticmethod
    def from_file(path: Path | str) -> Manifest:
        path = get_path(path, False)
        with open(path, 'rb') as file:
            return pickle.load(file)

    @staticmethod
    def from_directory(source: Path | str, checksum_algorithm: ChecksumAlg=None) -> Manifest:
        path = get_path(source, True)
        if not path.is_dir():
            raise ValueError(NOT_DIR.format(source))
        entries = []
        for subdir, _, files in os.walk(source):
            for file in files:
                root = Path(os.path.join(subdir, file))
                entry_path = root.relative_to(path)
                entries.append(
                    ManifestEntries.from_file_path(path,
                                                   entry_path,
                                                   checksum_algorithm=checksum_algorithm))
        return Manifest.model_validate({
            'root': str(path),
            'source': SourceType.PACKAGE,
            'summary': None,
            'entries': entries
            })

    @staticmethod
    def from_mets_file(source: Path | str) -> Manifest:
        path: Path = get_path(source, True)
        if not path.is_file():
            raise ValueError(NOT_FILE.format(source))
        mets_file = MetsFiles.from_file(path)
        entries: list[ManifestEntry] = list(map(ManifestEntries.from_file_entry,
                                                mets_file.file_entries))
        return Manifest.model_validate({
            'root': str(path),
            'source': SourceType.METS,
            'summary': None,
            'entries': entries
            })

def _test_checksums(path: Path, checksums: list[Checksum]) -> list[str]:
    issues: list[str] = []
    for checksum in checksums:
        calced_checksum = Checksummer(checksum.algorithm).hash_file(path)
        if not checksum == calced_checksum:
            issues.append(f'File {path} manifest checksum {checksum.value},' +
                          f'calculated checksum {calced_checksum}.')
    return issues

def _resolve_manifest_root(manifest: Manifest) -> Path:
    root: Path = Path(manifest.root)
    if manifest.source == SourceType.PACKAGE:
        return root
    if manifest.source == SourceType.METS:
        return root.parent
    raise ValueError(f'Unknown source type {manifest.source}')
