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
"""
E-ARK : Information package validation
        Command line validation application
"""
import argparse
from pprint import pprint
import os.path
import sys

import ip_validation.infopacks.structure as STRUCT

__version__ = '0.1.0'

defaults = {
    'description': """E-ARK Information Package validation (ip-check).
ip-check is a command-line tool to analyse and validate the structure and
metadata against the E-ARK Information Package specifications.
It is designed for simple integration into automated work-flows.""",
    'epilog': """
DILCIS Board (http://dilcis.eu)
See LICENSE for license information.
GitHub: https://github.com/E-ARK-Software/py-rest-ip-validator
Author: Carl Wilson (OPF), 2020
Maintainer: Carl Wilson (OPF), 2020"""
}

# Create PARSER
PARSER = argparse.ArgumentParser(description=defaults['description'], epilog=defaults['epilog'])

def parse_command_line():
    """Parse command line arguments."""
    # Add arguments
    PARSER.add_argument('-r', '--recurse',
                        action='store_true',
                        dest='inputRecursiveFlag',
                        default=True,
                        help='When analysing an information package recurse into representations.')
    PARSER.add_argument('-c', '--checksum',
                        action='store_true',
                        dest='inputChecksumFlag',
                        default=False,
                        help='Calculate and verify file checksums in packages.')
    PARSER.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='outputVerboseFlag',
                        default=False,
                        help='report results in verbose format')
    PARSER.add_argument('--version',
                        action='version',
                        version=__version__)
    PARSER.add_argument('files',
                        nargs='*',
                        default=[],
                        metavar='FILE',
                        help='Root IP folders or archived IPs to check.')

    # Parse arguments
    args = PARSER.parse_args()

    return args

def main():
    """Main command line application."""
    _exit = 0
    # Get input from command line
    args = parse_command_line()
    # If no target files or folders specified then print usage and exit
    if not args.files:
        PARSER.print_help()

    # Iterate the file arguments
    for file_arg in args.files:
        _loop_exit, results = _validate_ip(file_arg)
        _exit = _loop_exit if (_loop_exit > 0) else _exit
    sys.exit(_exit)

def _validate_ip(info_pack):
    ret_stat, to_validate = _get_ip_root(info_pack)
    struct_details = STRUCT.validate_package_structure(to_validate)
    pprint('Path {} is dir, struct result is: {}'.format(to_validate,
                                                         struct_details.status))
    for error in struct_details.errors:
        pprint(error.to_json())

    return ret_stat, struct_details

def _get_ip_root(info_pack):
    arch_processor = STRUCT.ArchivePackageHandler()
    # This is a var for the final source to validate
    to_validate = info_pack

    if not os.path.exists(info_pack):
        # Skip files that don't exist
        pprint('Path {} does not exist'.format(info_pack))
        return 1, None
    if os.path.isfile(info_pack):
        # Check if file is a archive format
        if not STRUCT.ArchivePackageHandler.is_archive(info_pack):
            # If not we can't process so report and iterate
            pprint('Path {} is not a file we can process.'.format(info_pack))
            return 2, None
        # Unpack the archive and set the source
        to_validate = arch_processor.unpack_package(info_pack)
    return 0, to_validate

# def _test_case_schema_checks():
if __name__ == '__main__':
    main()
