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
"""METS Schema validation."""
import fnmatch
import os

from lxml import etree

from importlib_resources import files

import ip_validation.infopacks.resources.schemas as SCHEMA

XLINK_NS = 'http://www.w3.org/1999/xlink'
METS_NS = 'http://www.loc.gov/METS/'
DILCIS_EXT_NS = 'https://DILCIS.eu/XML/METS/CSIPExtensionMETS'

class MetsValidator(object):
    """Encapsulates METS schema validation."""
    def __init__(self, root):
        self.validation_errors = []
        self.total_files = 0
        self.schema_mets = etree.XMLSchema(file=str(files(SCHEMA).joinpath('mets.xsd')))
        self.rootpath = root
        self.subsequent_mets = []

    def validate_mets(self, mets):
        '''
        Validates a Mets file. The Mets file is parsed with etree.iterparse(), which allows event-driven parsing of
        large files. On certain events/conditions actions are taken, like file validation or adding Mets files found
        inside representations to a list so that they will be evaluated later on.

        @param mets:    Path leading to a Mets file that will be evaluated.
        @return:        Boolean validation result.
        '''
        if mets.startswith('file://./'):
            mets = os.path.join(self.rootpath, mets[9:])
            # change self.rootpath so it fits any relative path found in the current (subsequent) mets
            self.rootpath = mets.rsplit('/', 1)[0]
        else:
            self.rootpath = mets.rsplit('/', 1)[0]

        try:
            parsed_mets = etree.iterparse(mets, events=('start', 'end'), schema=self.schema_mets)
            for event, element in parsed_mets:
                # Define what to do with specific tags.
                if event == 'end' and element.tag == q(METS_NS, 'file'):
                    # files
                    # self.total_files += 1
                    element.clear()
                    while element.getprevious() is not None:
                        del element.getparent()[0]
                elif event == 'end' and element.tag == q(METS_NS, 'div') and element.attrib['LABEL'].startswith('representations/'):
                    if fnmatch.fnmatch(element.attrib['LABEL'].rsplit('/', 1)[1], '*_mig-*'):
                        # representation mets files
                        rep = element.attrib['LABEL'].rsplit('/', 1)[1]
                        for child in element.getchildren():
                            if child.tag == q(METS_NS, 'mptr'):
                                metspath = child.attrib[q(XLINK_NS, 'href')]
                                sub_mets = rep, metspath
                                self.subsequent_mets.append(sub_mets)
                        element.clear()
                        while element.getprevious() is not None:
                            del element.getparent()[0]
                elif event == 'end' and element.tag == q(METS_NS, 'dmdSec'):
                    # dmdSec
                    pass
                elif event == 'end' and element.tag == q(METS_NS, 'amdSec'):
                    pass
        except etree.XMLSyntaxError as e:
            self.validation_errors.append(e)
        except BaseException as e:
            self.validation_errors.append(e)

        if self.total_files != 0:
            self.validation_errors.append('File count yielded %d instead of 0.' % self.total_files)

        if self.validation_errors and len(self.validation_errors) > 0:
            print('Error log for METS file: ', mets)
            for error in self.validation_errors:
                print(error)

        return True if len(self.validation_errors) == 0 else False

def q(ns, v):
    return '{{{}}}{}'.format(ns, v)
