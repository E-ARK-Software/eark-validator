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

import lxml.etree as ET

from eark_validator.ipxml.schema import Namespaces
from eark_validator.const import NO_PATH, NOT_DIR, NOT_FILE
from eark_validator.model import Checksum, ChecksumAlg

class Checksummer:
    def __init__(self, algorithm: ChecksumAlg | str):
        self._algorithm: ChecksumAlg = algorithm if isinstance(algorithm, ChecksumAlg) else ChecksumAlg.from_string(algorithm)

    @property
    def algorithm(self) -> ChecksumAlg:
        """Get the algorithm."""
        return self._algorithm

    def hash_file(self, path: str) -> 'Checksum':
        if (not os.path.exists(path)):
            raise FileNotFoundError(NO_PATH.format(path))
        if (not os.path.isfile(path)):
            raise ValueError(NOT_FILE.format(path))
        implemenation = ChecksumAlg.get_implementation(self._algorithm)
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                implemenation.update(chunk)
        return Checksum.model_validate({'algorithm': self._algorithm, 'value': implemenation.hexdigest()}, strict=True)

    @classmethod
    def from_mets_element(cls, element: ET.Element) -> 'Checksum':
        """Create a Checksum from an etree element."""
        # Get the child flocat element and grab the href attribute.
        algorithm = ChecksumAlg.from_string(element.attrib['CHECKSUMTYPE'])
        value = element.attrib['CHECKSUM']
        return Checksum.model_validate({'algorithm': algorithm, 'value': value}, strict=True)

    @classmethod
    def from_file(cls, path: str, algorithm: 'ChecksumAlg') -> 'Checksum':
        """Create a Checksum from an etree element."""
        # Get the child flocat element and grab the href attribute.
        return Checksummer(algorithm).hash_file(path)

class FileItem:
    def __init__(self, path: str, size: int, checksum: Checksum, mime: str):
        self._path = path
        self._size = size
        self._checksum = checksum
        self._mime = mime

    @property
    def path(self) -> str:
        """Get the path."""
        return self._path

    @property
    def name(self) -> str:
        """Get the name."""
        return os.path.basename(self._path)

    @property
    def size(self) -> int:
        """Get the size."""
        return self._size

    @property
    def checksum(self) -> Checksum:
        """Get the checksum value."""
        return self._checksum

    @property
    def mime(self) -> str:
        """Get the mime type."""
        return self._mime

    @classmethod
    def path_from_file_element(cls, element: ET.Element) -> str:
        return element.find(Namespaces.METS.qualify('FLocat'), namespaces=element.nsmap).attrib[Namespaces.XLINK.qualify('href')] if hasattr(element, 'nsmap') else element.find('FLocat').attrib['href']

    @classmethod
    def path_from_mdref_element(cls, element: ET.Element) -> 'FileItem':
        """Create a FileItem from a METS:mdRef etree element."""
        # Get the child flocat element and grab the href attribute.
        return element.attrib[Namespaces.XLINK.qualify('href')] if hasattr(element, 'nsmap') else element.find('FLocat').attrib['href']

    @classmethod
    def from_element(cls, element: ET.Element) -> 'FileItem':
        """Create a FileItem from an etree element."""
        path = ''
        if element.tag in [Namespaces.METS.qualify('file'), 'file']:
            path = cls.path_from_file_element(element)
        elif element.tag in [Namespaces.METS.qualify('mdRef'), 'mdRef']:
            path = cls.path_from_mdref_element(element)
        else:
            raise ValueError('Element {} is not a METS:file or METS:mdRef element.'.format(element.tag))
        size = int(element.attrib['SIZE'])
        mime = element.attrib['MIMETYPE']
        checksum = Checksummer.from_mets_element(element)
        return cls(path, size, checksum, mime)

    @classmethod
    def from_file_path(cls, path: str, mime:str=None, checksum_algorithm:ChecksumAlg | str=None) -> 'FileItem':
        """Create a FileItem from a file path."""
        if (not os.path.exists(path)):
            raise FileNotFoundError(NO_PATH.format(path))
        if (not os.path.isfile(path)):
            raise ValueError('Path {} is not a file.'.format(path))
        algorithm = checksum_algorithm if isinstance(checksum_algorithm, ChecksumAlg) else ChecksumAlg.from_string(checksum_algorithm)
        size = os.path.getsize(path)
        mimetype = mime or 'application/octet-stream'
        checksum = Checksummer.from_file(path, algorithm) if checksum_algorithm else None
        return cls(path, size, checksum, mimetype)

class Manifest:
    def __init__(self, root_path: str, file_items: dict[str, FileItem] or list[FileItem] = None):
        if (not os.path.exists(root_path)):
            raise FileNotFoundError(NO_PATH.format(root_path))
        if (not os.path.isdir(root_path)):
            raise ValueError(NOT_DIR.format(root_path))
        self._root_path = root_path
        self._file_items = file_items if isinstance(file_items, dict) else self._list_to_dict(root_path, file_items)

    @property
    def root_path(self) -> str:
        """Get the root path."""
        return self._root_path

    @property
    def file_count(self) -> int:
        """Get the number of files."""
        return len(self._file_items)

    @property
    def size(self) -> int:
        """Get the total file size in bytes."""
        return sum([item.size for item in self._file_items.values()])

    @property
    def items(self) -> dict[str, FileItem]:
        """Get the file items."""
        return self._file_items

    def get_item(self, path: str) -> FileItem or None:
        """Get a file item by path."""
        search_path = self._relative_path(self._root_path, path)
        return self._file_items.get(search_path)

    def check_integrity(self) -> tuple[bool, list[str]]:
        """Check the integrity of the manifest."""
        is_valid = True
        issues = []
        for item in self._file_items.values():
            abs_path = os.path.join(self._root_path, item.path)
            if (not os.path.isfile(abs_path)):
                is_valid = False
                issues.append('File {} is missing.'.format(item.path))
                continue
            if (item.size != os.path.getsize(abs_path)):
                issues.append('File {} manifest size {}, filesystem size {}.'.format(item.path, item.size, os.path.getsize(abs_path)))
                is_valid = False
            calced_checksum = Checksummer.from_file(abs_path, item.checksum.algorithm)
            if not item.checksum == calced_checksum:
                issues.append('File {} manifest checksum {}, calculated checksum {}.'.format(item.path, item.checksum, calced_checksum))
                is_valid = False
        return is_valid, issues

    @staticmethod
    def _relative_path(root_path: str, path: str) -> str:
        return path if not os.path.isabs(path) else os.path.relpath(path, root_path)

    @classmethod
    def from_directory(cls, root_path: str, checksum_algorithm: ChecksumAlg=None) -> 'Manifest':
        if (not os.path.exists(root_path)):
            raise FileNotFoundError(NO_PATH.format(root_path))
        if (not os.path.isdir(root_path)):
            raise ValueError(NOT_DIR.format(root_path))
        items = []
        for subdir, dirs, files in os.walk(root_path):
            for file in files:
                file_path = os.path.join(subdir, file)
                items.append(FileItem.from_file_path(file_path, checksum_algorithm=checksum_algorithm))
        return cls(root_path, items)

    @classmethod
    def from_file_items(cls, root_path: str, file_items: dict[str, FileItem] or list[FileItem]) -> 'Manifest':
        if (not os.path.exists(root_path)):
            raise FileNotFoundError(NO_PATH.format(root_path))
        if (not os.path.isdir(root_path)):
            raise ValueError(NOT_DIR.format(root_path))
        return cls(root_path, file_items)

    @classmethod
    def _list_to_dict(cls, root_path: str, file_items: list[FileItem]) -> dict[str, FileItem]:
        return {cls._relative_path(root_path, item.path): FileItem(cls._relative_path(root_path, item.path), item.size, item.checksum, item.mime) for item in file_items}
