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
"""Module containing tests covering the manifest class."""
from enum import Enum
import os
from pathlib import Path
import tempfile
import unittest
from importlib_resources import files
import xml.etree.ElementTree as ET

from eark_validator.model.manifest import Manifest, SourceType
from eark_validator.model.manifest import ManifestEntry

import tests.resources as RES
import tests.resources.xml as XML
import tests.resources.ips.unpacked as UNPACKED

from eark_validator.infopacks.manifest import (
    Checksummer,
    ManifestEntries,
    Manifests,
    _resolve_manifest_root
)
from eark_validator.mets import _parse_file_entry
from eark_validator.model import ChecksumAlg, Checksum


METS = 'METS.xml'
PERSON = 'person.xml'
DIR_PATH = Path(str(files(XML)))
PERSON_PATH = Path(os.path.join(DIR_PATH, PERSON))
MISSING_PATH = Path(os.path.join(DIR_PATH, 'missing.xml'))
FILE_XML = """
    <file ID="ID-A73FA446-1DC7-499A-BE1E-15B7AE09B3B3" MIMETYPE="application/ipxml" SIZE="3554" CREATED="2021-11-17T16:56:44.180Z" CHECKSUM="F37E90511B5DDE2E9C60378A0F0A0A1CF07145C8F12651E0E19731892C608DA7" CHECKSUMTYPE="SHA-256">
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
            alg = ChecksumAlg.from_string(value)
            self.assertIsNotNone(alg, 'Expected {} to be a valid checksum algorithm'.format(alg))

    def test_alg_names(self):
        """Test that checksums are present in HashAlgorithms."""
        alg_names = ['MD5', 'SHA1', 'SHA256', 'SHA384', 'SHA512']
        for name in alg_names:
            alg = ChecksumAlg.from_string(name)
            self.assertIsNotNone(alg)

    def test_alg_items(self):
        """Test that checksums are present in HashAlgorithms."""
        for alg_item in ChecksumAlg:
            alg = ChecksumAlg.from_string(alg_item)
            self.assertIsNotNone(alg)

    def test_missing_alg(self):
        """Test that a missing algorithm raises a ValueError."""
        with self.assertRaises(ValueError):
            ChecksumAlg.from_string('NOT_AN_ALGORITHM')

    def test_missing_implementation(self):
        """Test that a missing algorithm returns None."""
        with self.assertRaises(ValueError):
            ChecksumAlg.get_implementation(FakeEnum.FAKE)

class ChecksummerTest(unittest.TestCase):
    def test_from_alg(self):
        """Test that a checksum algorithm is returned."""
        alg = ChecksumAlg.from_string('MD5')
        summer = Checksummer(alg)
        self.assertEqual(summer.algorithm, alg)

    def test_from_string_name(self):
        """Test that a checksum algorithm is returned."""
        summer = Checksummer('SHA1')
        self.assertEqual(summer.algorithm, ChecksumAlg.SHA1)

    def test_from_string_value(self):
        """Test that a checksum algorithm is returned."""
        summer = Checksummer('SHA-1')
        self.assertEqual(summer.algorithm, ChecksumAlg.SHA1)

    def test_md5(self):
        """Test MD5 calculation by HashAlgorithms."""
        summer = Checksummer(ChecksumAlg.from_string('MD5'))
        digest = summer.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'MD5', 'Expected MD5 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, '9958111AF1284696D07EC9D2E70D2517', 'MD5 digest {} does not match'.format(digest.value))

    def test_sha1(self):
        """Test SHA1 calculation by HashAlgorithms."""
        alg = Checksummer(ChecksumAlg.from_string('SHA1'))
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA1', 'Expected SHA1 digest id, not {}'.format(digest.algorithm.name))
        self.assertNotEqual(digest.value, 'ed294aaff253f66e4f1c839b732a43f36ba91677', 'SHA1 digest {} does not match'.format(digest.value))
        self.assertEqual(Checksum(algorithm=ChecksumAlg.SHA1, value='ed294aaff253f66e4f1c839b732a43f36ba91677'), digest, 'Digest {} does not match'.format(digest.value))
        self.assertEqual(Checksum.model_validate({'algorithm': ChecksumAlg.SHA1, 'value': 'ed294aaff253f66e4f1c839b732a43f36ba91677'}, strict=True), digest, 'SHA1 digest {} does not match'.format(digest.value))

    def test_sha256(self):
        """Test SHA256 calculation by HashAlgorithms."""
        alg = Checksummer(ChecksumAlg.from_string('SHA256'))
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA256', 'Expected SHA256 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, 'C944AF078A5AC0BAC02E423D663CF6AD2EFBF94F92343D547D32907D13D44683', 'SHA256 digest {} does not match'.format(digest.value))

    def test_sha384(self):
        """Test SHA384 calculation by HashAlgorithms."""
        alg = Checksummer(ChecksumAlg.from_string('SHA384'))
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA384', 'Expected SHA384 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, 'AA7AF70D126E215013C8E335EADA664379E1947BF7A194672AF3DBC529D82E9ADB0B4F5098BDDED9AABA83439AD9BEE9', 'SHA384 digest {} does not match'.format(digest.value))

    def test_sha512(self):
        """Test SHA512 calculation by HashAlgorithms."""
        alg = Checksummer(ChecksumAlg.from_string('SHA512'))
        digest = alg.hash_file(PERSON_PATH)
        self.assertEqual(digest.algorithm.name, 'SHA512', 'Expected SHA512 digest id, not {}'.format(digest.algorithm.name))
        self.assertEqual(digest.value, '04E2B2A51FCBF8B26A88A819723F928D2AEE2FD3342BED090571FC2DE3C9C2D2ED7B75545951BA3A4A7F5E4BD361544ACCBCD6E3932DC0D26FCAF4DADC79512B', 'MSHA512D5 digest {} does not match'.format(digest.value))

    def test_dir_error(self):
        alg = Checksummer(ChecksumAlg.from_string('MD5'))
        with self.assertRaises(ValueError):
            alg.hash_file(DIR_PATH)

    def test_missing_error(self):
        alg = Checksummer(ChecksumAlg.from_string('MD5'))
        with self.assertRaises(FileNotFoundError):
            alg.hash_file(MISSING_PATH)

class ManifestEntryTest(unittest.TestCase):
    def test_from_missing_path(self):
        with self.assertRaises(FileNotFoundError):
            ManifestEntries.from_file_path(Path('/none'), MISSING_PATH)

    def test_from_dir_path(self):
        with self.assertRaises(ValueError):
            ManifestEntries.from_file_path(DIR_PATH, DIR_PATH)

    def test_from_file(self):
        item = ManifestEntries.from_file_path(PERSON_PATH, PERSON_PATH, 'SHA256')
        self.assertEqual(item.checksums[0].algorithm.value, 'SHA-256', 'Expected SHA-256 digest value not {}'.format(item.checksums[0].algorithm.value))
        self.assertEqual(item.checksums[0].value, 'C944AF078A5AC0BAC02E423D663CF6AD2EFBF94F92343D547D32907D13D44683', 'SHA256 digest {} does not match'.format(item.checksums[0].value))

    def test_from_file_entry(self):
        entry: ManifestEntry = ManifestEntries.from_file_entry(_parse_file_entry(ET.fromstring(FILE_XML)))
        self.assertEqual(entry.checksums[0].algorithm, ChecksumAlg.SHA256)
        self.assertEqual(entry.checksums[0].value, 'F37E90511B5DDE2E9C60378A0F0A0A1CF07145C8F12651E0E19731892C608DA7')
        self.assertEqual(str(entry.path), 'representations/rep1/METS.xml')
        self.assertEqual(entry.size, 3554)

class ManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._manifest = Manifests.from_directory(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031'), 'MD5')

    def setUp(self):
        self._test_dir = tempfile.TemporaryDirectory()
        self._temp_man_pickle = os.path.join(self._test_dir.name, 'manifest.pickle')

    def tearDown(self):
        self._test_dir.cleanup()

    def test_items(self):
        self.assertEqual(len(self._manifest.entries), self._manifest.file_count)

    def test_validate_manifest(self):
        is_valid, _ = Manifests.validate_manifest(self._manifest)
        self.assertTrue(is_valid)

    def test_no_dir(self):
        missing = str(files(UNPACKED).joinpath('missing'))
        with self.assertRaises(FileNotFoundError):
            Manifests.from_directory(missing)

    def test_file_path(self):
        file_path = str(files(RES).joinpath('empty.file'))
        with self.assertRaises(ValueError):
            Manifests.from_directory(file_path)
        with self.assertRaises(ValueError):
            Manifests.from_mets_file(file_path)

    def test_manifest_filecount(self):
        self.assertEqual(self._manifest.file_count, 23)

    def test_manifest_size(self):
        self.assertEqual(self._manifest.total_size, 306216)

    def test_from_missing_source(self):
        missing = str(files(UNPACKED).joinpath('missing'))
        with self.assertRaises(FileNotFoundError):
            Manifests.from_source(missing, 'MD5')

    def test_from_package_source(self):
        manifest = Manifests.from_source(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031'), 'MD5')
        self.assertEqual(manifest.source, SourceType.PACKAGE)
        is_valid, _ = Manifests.validate_manifest(manifest)
        self.assertTrue(is_valid)

    def test_from_mets_source(self):
        manifest = Manifests.from_source(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031').joinpath(METS), 'MD5')
        self.assertEqual(manifest.source, SourceType.METS)
        is_valid, _ = Manifests.validate_manifest(manifest)
        self.assertTrue(is_valid)

    def test_from_missing_mets_file(self):
        with self.assertRaises(FileNotFoundError):
            Manifests.from_mets_file(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031').joinpath('missing_mets.xml'))

    def test_from_dir_mets_file(self):
        with self.assertRaises(ValueError):
            Manifests.from_mets_file(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031'))

    def test_to_file(self):
        Manifests.to_file(self._manifest, self._temp_man_pickle)
        self.assertTrue(os.path.exists(self._temp_man_pickle))

    def test_from_file(self):
        Manifests.to_file(self._manifest, self._temp_man_pickle)
        manifest: Manifest = Manifests.from_file(self._temp_man_pickle)
        is_valid, _ = Manifests.validate_manifest(manifest, files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031'))
        self.assertTrue(is_valid)
        is_valid, errors = Manifests.validate_manifest(manifest, files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031-bad'))
        self.assertFalse(is_valid)
        self.assertEqual(len(errors), 3)

    def test_resolve_manifest_bad_source(self):
        manifest = Manifest.model_validate({
            'root': str(files(UNPACKED).joinpath('733dc055-34be-4260-85c7-5549a7083031')),
            'source': SourceType.UNKNOWN
            })
        with self.assertRaises(ValueError):
            _resolve_manifest_root(manifest)
