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
"""Structural requirements as a dictionary."""

from eark_validator.model import Level


REQUIREMENTS = {
    1: {
          'id': 'CSIPSTR1',
          'level': Level.MUST,
          'message': ' '.join([
            'Any Information Package MUST be included within a single physical root',
            'folder (known as the “Information Package root folder”). For packages contained',
            'in an archive format, see CSIPSTR3, the archive MUST unpack to a single root folder.'
          ])
        },
    2: {
          'id': 'CSIPSTR2',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The Information Package root folder SHOULD be named with the ID or name of',
            'the Information Package, that is the value of the package METS.xml\'s root <mets>',
            'element\'s @OBJID attribute.'
          ])
        },
    3: {
          'id': 'CSIPSTR3',
          'level': Level.MAY,
          'message': ' '.join([
            'The Information Package MAY be contained in an archive/compressed form,',
            'e.g. TAR or ZIP, for storage or transfer. The specific format details should be',
            'decided by the interested parties and documented, for example in a submission',
            'agreement or statement of access terms.'
          ])
        },
    4: {
          'id': 'CSIPSTR4',
          'level': Level.MUST,
          'message': ' '.join([
            'The Information Package root folder MUST include a file named METS.xml.',
            'This file MUST contain metadata that identifies the package, provides a high-level',
            'package description, and describes its structure, including pointers to constituent',
            'representations.'
          ])
        },
    5: {
          'id': 'CSIPSTR5',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The Information Package root folder SHOULD include a folder named',
            'metadata, which SHOULD include metadata relevant to the whole package.'
          ])
        },
    6: {
          'id': 'CSIPSTR6',
          'level': Level.SHOULD,
          'message': ' '.join([
            'If preservation metadata are available they SHOULD be included in',
            'sub-folder preservation.'
          ])
        },
    7: {
          'id': 'CSIPSTR7',
          'level': Level.SHOULD,
          'message': ' '.join([
            'If descriptive metadata are available, they SHOULD be included in',
            'sub-folder descriptive.'
          ])
        },
    8: {
          'id': 'CSIPSTR8',
          'level': Level.MAY,
          'message': ' '.join([
            'If any other metadata are available, they MAY be included in separate',
            'sub-folders, for example an additional folder named other.'
          ])
       },
    9: {
          'id': 'CSIPSTR9',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The Information Package folder SHOULD include a folder named',
            'representations.'
          ])
       },
    10: {
          'id': 'CSIPSTR10',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The representations folder SHOULD include a sub-folder for each',
            'individual representation (i.e. the “representation folder”). Each representation',
            'folder should have a string name that is unique within the package scope. For',
            'example the name of the representation and/or its creation date might be good',
            'candidates as a representation sub-folder name.'
          ])
        },
    11: {
          'id': 'CSIPSTR11',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The representation folder SHOULD include a sub-folder named data',
            'which MAY include all data constituting the representation.'
          ])
        },
    12: {
          'id': 'CSIPSTR12',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The representation folder SHOULD include a metadata file named METS.xml',
            'which includes information about the identity and structure of the representation',
            'and its components. The recommended best practice is to always have a METS.xml in',
            'the representation folder.'
          ])
        },
    13: {
          'id': 'CSIPSTR13',
          'level': Level.SHOULD,
          'message': ' '.join([
            'The representation folder SHOULD include a sub-folder named metadata',
            'which MAY include all metadata about the specific representation.'
          ])
        },
    14: {
          'id': 'CSIPSTR14',
          'level': Level.MAY,
          'message': 'The Information Package MAY be extended with additional sub-folders.'
        },
    15: {
          'id': 'CSIPSTR15',
          'level': Level.SHOULD,
          'message': ' '.join([
            'We recommend including all XML schema documents for any structured',
            'metadata within package. These schema documents SHOULD be placed in a sub-folder',
            'called schemas within the Information Package root folder and/or the representation',
            'folder.'
          ])
        },
    16: {
          'id': 'CSIPSTR16',
          'level': Level.SHOULD,
          'message': ' '.join([
            'We recommend including any supplementary documentation for the package',
            'or a specific representation within the package. Supplementary documentation SHOULD',
            'be placed in a sub-folder called documentation within the Information Package root',
            'folder and/or the representation folder. Examples of documentation include',
            'representation information and manuals for the system the data objects have been',
            'exported from.'
          ])
        }
}
