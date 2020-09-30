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
"""Simple definition of package structure errors."""
from ip_validation.infopacks.rules import Severity

STRUCT_ERRORS = {
    1: """Any Information Package MUST be included within a single physical root
       folder (known as the “Information Package root folder”). For packages
       presented in an archive format, see CSIPSTR3, the archive MUST unpack to
       a single root folder.""",
    2: """The Information Package root folder SHOULD be named with the ID or
       name of the Information Package, that is the value of the package
       METS.xml’s root <mets> element’s @OBJID attribute.""",
    3: """The Information Package root folder MAY be compressed (for example by
       using TAR or ZIP). Which specific compression format to use needs to be
       stated in the Submission Agreement.""",
    4: """The Information Package root folder MUST include a file named
       METS.xml. This file MUST contain metadata that identifies the package,
       provides a high-level package description, and describes its structure,
       including pointers to constituent representations.""",
    5: """The Information Package root folder SHOULD include a folder named
       metadata, which SHOULD include metadata relevant to the whole package.""",
    6: """If preservation metadata are available, they SHOULD be included in
       sub-folder preservation.""",
    7: """If descriptive metadata are available, they SHOULD be included in
       sub-folder descriptive.""",
    8: """If any other metadata are available, they MAY be included in
       separate sub-folders, for example an additional folder named other.""",
    9: """The Information Package folder SHOULD include a folder named
       representations.""",
    10: """The representations folder SHOULD include a sub-folder for each
        individual representation (i.e. the “representation folder”). Each
        representation folder should have a string name that is unique within
        the package scope. For example the name of the representation and/or its
        creation date might be good candidates as a representation sub-folder
        name.""",
    11: """The representation folder SHOULD include a sub-folder named data
        which MAY include all data constituting the representation.""",
    12: """The representation folder SHOULD include a metadata file named
        METS.xml which includes information about the identity and structure of
        the representation and its components. The recommended best practice is
        to always have a METS.xml in the representation folder.""",
    13: """The representation folder SHOULD include a sub-folder named metadata
        which MAY include all metadata about the specific representation.""",
    14: """The Information Package MAY be extended with additional sub-folders.""",
    15: """We recommend including all XML schema documents for any structured
        metadata within package. These schema documents SHOULD be placed in a
        sub-folder called schemas within the Information Package root folder
        and/or the representation folder.""",
    16: """We recommend including any supplementary documentation for the
        package or a specific representation within the package. Supplementary
        documentation SHOULD be placed in a sub-folder called documentation
        within the Information Package root folder and/or the representation
        folder."""
}

class StructError():
    """Encapsulates an individual validation test result."""
    def __init__(self, rule_id, severity, message, sub_message):
        self._rule_id = rule_id
        self.severity = severity
        self._message = message
        self._sub_message = sub_message

    @property
    def rule_id(self):
        """Get the rule_id."""
        return self._rule_id

    @property
    def severity(self):
        """Get the severity."""
        return self._severity

    @severity.setter
    def severity(self, value):
        if not value in list(Severity):
            raise ValueError("Illegal severity value")
        self._severity = value

    @property
    def is_error(self):
        """Returns True if this is an error message, false otherwise."""
        return self.severity == Severity.Error

    @property
    def is_info(self):
        """Returns True if this is an info message, false otherwise."""
        return self.severity == Severity.Info

    @property
    def is_warning(self):
        """Returns True if this is an warning message, false otherwise."""
        return self.severity == Severity.Warn

    @property
    def message(self):
        """Get the message."""
        return self._message

    @property
    def sub_message(self):
        """Get the sub-message."""
        return self._sub_message

    def to_json(self):
        """Output the message in JSON format."""
        return {"rule_id" : self.rule_id, "severity" : str(self.severity.name),
                "message" : self.message, "sub_message" : self.sub_message}

    @classmethod
    def from_values(cls, rule_id, severity=Severity.Error, sub_message=''):
        """Create an StructError from values supplied."""
        return StructError('CSIPSTR{}'.format(rule_id), severity,
                           STRUCT_ERRORS.get(rule_id), sub_message)
