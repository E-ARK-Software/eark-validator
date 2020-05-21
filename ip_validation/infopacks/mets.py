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
import os

from lxml import etree

XLINK_NS = "http://www.w3.org/1999/xlink"
METS_NS = 'http://www.loc.gov/METS/'

class MetsValidator(object):
    """Encapsulates METS schema validation."""
    def __init__(self, root, mets_schema_file=os.path.join(ROOT, "eatb/resources/schemas/IP.xsd"),
                 premis_schema_file=os.path.join(ROOT, "eatb/resources/schemas/premis-v2-2.xsd")):
        self.validation_errors = []
        self.total_files = 0
        self.schema_mets = etree.XMLSchema(file=mets_schema_file)
        self.schema_premis = etree.XMLSchema(file=premis_schema_file)
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
                    self.total_files += 1
                    self.validate_file(element)
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
                    # pass
                    if len(element.getchildren()) > 0:
                        for child in element.getchildren():
                            # child are: digiprovMD
                            if len(child.getchildren()) > 0:
                                for sub_child in child.getchildren():
                                    # sub_child are: mdRef
                                    if sub_child.tag == etree.Comment or sub_child.tag == etree.PI:  # filter out comments (they also count as children)
                                        pass
                                    elif sub_child.attrib['MDTYPE'] == 'PREMIS':
                                        if sub_child.attrib[q(XLINK_NS, 'href')].startswith('file://./'):
                                            rel_path = sub_child.attrib[q(XLINK_NS, 'href')]
                                            premis = os.path.join(self.rootpath, rel_path[9:])
                                            try:
                                                parsed_premis = etree.iterparse(premis, events=('start',), schema=self.schema_premis)
                                                for event, el in parsed_premis:
                                                    # What to do here?
                                                    pass
                                                print('Successfully validated Premis file: %s' % premis)

                                            except etree.XMLSyntaxError as e:
                                                print('VALIDATION ERROR: The Premis file %s yielded errors:' % premis)
                                                print(e)
                                                self.validation_errors.append(e)
                                        else:
                                            pass
                                    else:
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


    def validate_file(self, file):
        '''
        Validates every file found inside a Mets, so far: size, checksum, fixity. If a file exists, the counter for
        self.total_files is diminished.

        @param file:    XML Element of a file that will be validated.
        @return:
        '''
        err = []
        log = []

        # get information about the file
        for child in file.getchildren():
            if child.tag == etree.Comment or child.tag == etree.PI:
                # skip if it's an XML comment
                pass
            elif child.tag == q(METS_NS, 'FLocat'):
                attr_path = child.attrib[q(XLINK_NS, 'href')]
        attr_size = file.attrib['SIZE']
        attr_checksum = file.attrib['CHECKSUM'].lower() # just in case someone creates a checksum with uppercase letters
        attr_checksumtype = file.attrib['CHECKSUMTYPE']
        # mimetpye = file.attrib['MIMETYPE']

        # check if file exists, if yes validate it
        fitem = remove_protocol(attr_path)
        file_path = os.path.join(self.rootpath, fitem).replace('\\', '/')

        if not os.path.exists(file_path):
            err.append("Unable to find file referenced in METS: %s" % file_path)
        else:
            self.total_files -= 1
            # check if file size is valid
            # TODO: is this even needed?
            file_size = os.path.getsize(file_path)
            if not int(file_size) == int(attr_size):
                err.append("Actual file size %s does not equal file size attribute value %s, file: %s" % (file_size, attr_size, file_path))
                # workaround for conduit.log in AIP metadata/ folder on IP root level
                if file_path[-22:] == './metadata/conduit.log':
                    err.pop()
                    log.append('Forced validation result \'True\' for file: %s' % (file_path))

            # validate checksum
            checksum_validation = ChecksumValidation()
            checksum_result = checksum_validation.validate_checksum(file_path, attr_checksum, attr_checksumtype)

            # workaround for conduit.log in AIP metadata/ folder on IP root level
            if file_path[-22:] == './metadata/conduit.log':
                checksum_result = True

            if not checksum_result == True:
                err.append('Checksum validation failed for: %s' % file_path)

        for error in err:
            print('File validation error: ' + error)
            self.validation_errors.append(error)
