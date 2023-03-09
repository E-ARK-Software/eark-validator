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

import unittest

from importlib_resources import files

import tests.resources.xml as XML

from ip_validation.xml import namespaces as NS

class MetsValidatorTest(unittest.TestCase):
    """Tests for Schematron validation rules."""
    def test_from_prefix(self):
        for namespace in NS.Namespaces:
            self.assertEqual(namespace, NS.Namespaces.from_prefix(namespace.prefix))

    def test_from_id(self):
        for namespace in NS.Namespaces:
            self.assertEqual(namespace, NS.Namespaces.from_id(namespace.id))

    def test_qualify(self):
        for namespace in NS.Namespaces:
            self.assertEqual('{{{}}}file'.format(namespace.id), namespace.qualify('file'))


if __name__ == '__main__':
    unittest.main()
