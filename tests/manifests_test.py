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
"""Module containing tests covering the manifest class."""
from enum import Enum
import os
import unittest
from importlib_resources import files
import xml.etree.ElementTree as ET

import tests.resources.xml as XML
import tests.resources.ips.unpacked as UNPACKED

from ip_validation.infopacks.manifest import (
    HashAlgorithms,
    FileItem,
    Checksum,
    Manifest
)

METS = 'METS.xml'
PERSON = 'person.xml'
DIR_PATH = str(files(XML))
PERSON_PATH = os.path.join(DIR_PATH, PERSON)
MISSING_PATH = os.path.join(DIR_PATH, 'missing.xml')
FILE_XML = """
    <file ID="ID-A73FA446-1DC7-499A-BE1E-15B7AE09B3B3" MIMETYPE="application/xml" SIZE="3554" CREATED="2021-11-17T16:56:44.180Z" CHECKSUM="F37E90511B5DDE2E9C60378A0F0A0A1CF07145C8F12651E0E19731892C608DA7" CHECKSUMTYPE="SHA-256">
        <FLocat type="simple" href="representations/rep1/METS.xml" LOCTYPE="URL"/>
    </file>"""

class FakeEnum(Enum):
    """Fake enum for testing."""
    FAKE = 'fake'

class ChecksumTest(unittest.TestCase):
    def test_alg_values(self):
        """Test that checksums are present in HashAlgorithms."""
        alg_values = ['MD5', 'SHA-1', 'SHA-256', 'SHA-384', 'SHA-512']
        for value in alg_values:
            alg = HashAlgorithms.from_string(value)
            self.assertIsNotNone(alg)

    def test_alg_names(self):
        """Test that checksums are present in HashAlgorithms."""
        alg_names = ['MD5', 'SHA1', 'SHA256', 'SHA384', 'SHA512']
        for name in alg_names:
            alg = HashAlgorithms.from_string(name)
            self.assertIsNotNone(alg)

    def test_alg_items(self):
        """Test that checksums are present in HashAlgorithms."""
        for alg_item in HashAlgorithms:
            alg = HashAlgorithms.from_string(alg_item)
            self.assertIsNotNone(alg)

    def test_missing_alg(self):
        """Test that a missing algorithm returns None."""
        alg = HashAlgorithms.from_string('NOT_AN_ALGORITHM')
        self.assertIsNone(alg)

    def test_missing_implementation(self):
        """Test that a missing algorithm returns None."""
        with self.assertRaises(ValueError):
            HashAlgorithms.get_implementation(FakeEnum.FAKE)

    def test_md5(self):
        """Test MD5 calculation by HashAlgorithms."""
        alg = HashAlgorithms.from_string('MD5')
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'MD5', 'Expected MD5 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, '9958111af1284696d07ec9d2e70d2517', 'MD5 digest {} does not match'.format(digest.value))

    def test_sha1(self):
        """Test SHA1 calculation by HashAlgorithms."""
        alg = HashAlgorithms.from_string('SHA1')
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA1', 'Expected SHA1 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, 'ed294aaff253f66e4f1c839b732a43f36ba91677', 'SHA1 digest {} does not match'.format(digest.value))

    def test_sha256(self):
        """Test SHA256 calculation by HashAlgorithms."""
        alg = HashAlgorithms.from_string('SHA256')
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA256', 'Expected SHA256 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, 'c944af078a5ac0bac02e423d663cf6ad2efbf94f92343d547d32907d13d44683', 'SHA256 digest {} does not match'.format(digest.value))

    def test_sha384(self):
        """Test SHA384 calculation by HashAlgorithms."""
        alg = HashAlgorithms.from_string('SHA384')
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA384', 'Expected SHA384 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, 'aa7af70d126e215013c8e335eada664379e1947bf7a194672af3dbc529d82e9adb0b4f5098bdded9aaba83439ad9bee9', 'SHA384 digest {} does not match'.format(digest.value))

    def test_sha512(self):
        """Test SHA512 calculation by HashAlgorithms."""
        alg = HashAlgorithms.from_string('SHA512')
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA512', 'Expected SHA512 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, '04e2b2a51fcbf8b26a88a819723f928d2aee2fd3342bed090571fc2de3c9c2d2ed7b75545951ba3a4a7f5e4bd361544accbcd6e3932dc0d26fcaf4dadc79512b', 'MSHA512D5 digest {} does not match'.format(digest.value))

    def test_dir_error(self):
        alg = HashAlgorithms.from_string('MD5')
        with self.assertRaises(ValueError):
            alg.hash_file(DIR_PATH)

    def test_missing_error(self):
        alg = HashAlgorithms.from_string('MD5')
        with self.assertRaises(FileNotFoundError):
            alg.hash_file(MISSING_PATH)

    def test_from_xml(self):
        element = ET.fromstring(FILE_XML)
        checksum = Checksum.from_mets_element(element)
        self.assertEqual(checksum.algorithm, HashAlgorithms.SHA256)
        self.assertTrue(checksum.is_value('F37E90511B5DDE2E9C60378A0F0A0A1CF07145C8F12651E0E19731892C608DA7'))

class FileItemTest(unittest.TestCase):
    def test_from_path(self):
        item = FileItem.from_file_path(PERSON_PATH)
        self.assertEqual(item.path, PERSON_PATH)
        self.assertEqual(item.name, PERSON)
        self.assertEqual(item.size, 75)
        self.assertEqual(item.mime, 'application/octet-stream')
        self.assertIsNone(item.checksum)

    def test_from_path_with_mime(self):
        item = FileItem.from_file_path(PERSON_PATH, mime='text/xml')
        self.assertEqual(item.path, PERSON_PATH)
        self.assertEqual(item.name, PERSON)
        self.assertEqual(item.size, 75)
        self.assertEqual(item.mime, 'text/xml')
        self.assertIsNone(item.checksum)

    def test_from_path_with_checksum(self):
        item = FileItem.from_file_path(PERSON_PATH, checksum_algorithm='MD5')
        self.assertEqual(item.path, PERSON_PATH)
        self.assertEqual(item.name, PERSON)
        self.assertEqual(item.size, 75)
        self.assertIsNotNone(item.checksum)
        self.assertEqual(item.checksum.algorithm.name, 'MD5', 'Expected MD5 digest id, not {}'.format(item.checksum.algorithm.name))
        self.assertEqual(item.checksum.value, '9958111af1284696d07ec9d2e70d2517', 'MD5 digest {} does not match'.format(item.checksum.value))

    def test_dir_path(self):
        with self.assertRaises(ValueError):
            FileItem.from_file_path(DIR_PATH)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            FileItem.from_file_path(MISSING_PATH)

    def test_from_xml(self):
        element = ET.fromstring(FILE_XML)
        file_item = FileItem.from_element(element)
        self.assertEqual(file_item.path, 'representations/rep1/METS.xml')
        self.assertEqual(file_item.name, METS)
        self.assertEqual(file_item.size, 3554)
        self.assertEqual(file_item.checksum.algorithm, HashAlgorithms.SHA256)
        self.assertTrue(file_item.checksum.is_value('F37E90511B5DDE2E9C60378A0F0A0A1CF07145C8F12651E0E19731892C608DA7'))

class ManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._manifest = Manifest.from_directory(str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')), 'MD5')

    def test_root_dir(self):
        self.assertEqual(self._manifest.root_path, str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')))

    def test_items(self):
        self.assertEqual(len(self._manifest.items), self._manifest.file_count)

    def test_no_dir(self):
        missing = str(files(UNPACKED).joinpath('missing'))
        with self.assertRaises(FileNotFoundError):
            Manifest(missing, [])
        with self.assertRaises(FileNotFoundError):
            Manifest.from_directory(missing)
        with self.assertRaises(FileNotFoundError):
            Manifest.from_file_items(missing, [])

    def test_file_path(self):
        file_path = str(files(UNPACKED).joinpath('single_file').joinpath('empty.file'))
        with self.assertRaises(ValueError):
            Manifest(file_path, [])
        with self.assertRaises(ValueError):
            Manifest.from_directory(file_path)
        with self.assertRaises(ValueError):
            Manifest.from_file_items(file_path, [])

    def test_manifest_filecount(self):
        self.assertEqual(self._manifest.file_count, 23)

    def test_manifest_size(self):
        self.assertEqual(self._manifest.size, 306486)

    def test_manifest_get_rel_file(self):
        mets_file = self._manifest.get_item(METS)
        self.assertIsNotNone(mets_file, 'METS.xml not found in via relative path')
        mets_file = self._manifest.get_item('representations/rep1/data/RODA-in.png')
        self.assertIsNotNone(mets_file, 'representations/rep1/data/RODA-in.png not found in via relative path')

    def test_manifest_get_abs_file(self):
        mets_file = self._manifest.get_item(os.path.join(str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')), METS))
        self.assertIsNotNone(mets_file, 'METS.xml not found using absolute path')
        mets_file = self._manifest.get_item(os.path.join(str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')), 'representations/rep1/data/RODA-in.png'))
        self.assertIsNotNone(mets_file, 'representations/rep1/data/RODA-in.png not found using absolute path')
