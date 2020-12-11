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
"""
E-ARK : Information package validation
        Command line validation application
"""
import argparse
from pprint import pprint
import os.path
import sys

import ip_validation.cli.testcases as TC
import ip_validation.infopacks.information_package as IP

__version__ = "0.1.0"

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
    PARSER.add_argument('--testcase', '-t',
                        action="store_true",
                        dest="testCase",
                        default=False,
                        help="Treat [FILE]s as XML test cases and drive validation from those.")
    PARSER.add_argument('--recurse', '-r',
                        action="store_true",
                        dest="inputRecursiveFlag",
                        default=True,
                        help="When analysing an information package recurse into representations.")
    PARSER.add_argument('--checksum', '-c',
                        action="store_true",
                        dest="inputChecksumFlag",
                        default=False,
                        help="Calculate and verify file checksums in packages.")
    PARSER.add_argument('--verbose', '-v',
                        action="store_true",
                        dest="outputVerboseFlag",
                        default=False,
                        help="report results in verbose format")
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
    # Get input from command line
    args = parse_command_line()
    # If no target files or folders specified then print usage and exit
    if not args.files:
        PARSER.print_help()
        sys.exit(0)

    # Iterate the file arguments
    for file_arg in args.files:
        if args.testCase:
            _validate_test_case(file_arg)
        else:
            _validate_ip(file_arg)

def _validate_ip(info_pack):
    arch_processor = IP.ArchivePackageHandler()
    # This is a var for the final source to validate
    to_validate = info_pack

    if not os.path.exists(info_pack):
        # Skip files that don't exist
        pprint('Path {} does not exist'.format(info_pack))
        return
    if os.path.isfile(info_pack):
        # Check if file is a archive format
        if not IP.ArchivePackageHandler.is_archive(info_pack):
            # If not we can't process so report and iterate
            pprint('Path {} is not a file we can process.'.format(info_pack))
            return
        # Unpack the archive and set the source
        to_validate = arch_processor.unpack_package(info_pack)

    struct_details = IP.validate_package_structure(to_validate)
    pprint('Path {} is dir, struct result is: {}'.format(to_validate,
                                                         struct_details.package_status))
    for error in struct_details.errors:
        pprint(error.to_json())

def _validate_test_case(test_case):
    case = TC.TestCase.from_xml_file(test_case)
    if not case.testable:
        if not case.unknown:
            # don't ouput UNKNOWN testablitiy test cases, do output FALSE cases
            pprint('{}:{} not testable.'.format(case.case_id.specification,
                                                  case.case_id.requirement_id))
        sys.exit(0)
    for rule in case.rules:
        for package in rule.packages:
            package_path = os.path.join(os.path.dirname(test_case), package.name)
            _validate_ip(package_path)
    sys.exit(1)

# def _test_case_schema_checks():


if __name__ == "__main__":
    main()
