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
import os.path
from pathlib import Path
import sys
from typing import Optional, Tuple
import importlib.metadata

import argparse
from rich import print

from eark_validator.model import ValidationReport
import eark_validator.packages as PACKAGES
from eark_validator.infopacks.package_handler import PackageHandler

__version__ = importlib.metadata.version('eark_validator')

defaults = {
    'description': """E-ARK Information Package validation (eark-validator).
eark-validator is a command-line tool to analyse and validate the structure and
metadata against the E-ARK Information Package specifications.
It is designed for simple integration into automated work-flows.""",
    'epilog': """
DILCIS Board (http://dilcis.eu)
See LICENSE for license information.
GitHub: https://github.com/E-ARK-Software/eark-validator
Author: Carl Wilson (OPF), 2020-2024
Maintainer: Carl Wilson (OPF), 2020-2024"""
}

# Create PARSER
PARSER = argparse.ArgumentParser(prog='eark-validator', description=defaults['description'], epilog=defaults['epilog'])

def parse_command_line():
    """Parse command line arguments."""
    # Add arguments
    PARSER.add_argument('-r', '--recurse',
                        action='store_true',
                        dest='inputRecursiveFlag',
                        default=False,
                        help='When analysing an information package recurse into representations.')
    PARSER.add_argument('-c', '--checksum',
                        action='store_true',
                        dest='inputChecksumFlag',
                        default=False,
                        help='Calculate and verify package checksums.')
    PARSER.add_argument('-m', '--manifest',
                        action='store_true',
                        dest='inputManifestFlag',
                        default=False,
                        help='Display package manifest information.')
    PARSER.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='outputVerboseFlag',
                        default=False,
                        help='Verbose reporting for selected output options.')
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
        _loop_exit, _ = _validate_ip(file_arg)
        _exit = _loop_exit if (_loop_exit > 0) else _exit
    sys.exit(_exit)

def _validate_ip(path: str) -> Tuple[int, Optional[ValidationReport]]:
    ret_stat, checked_path = _check_path(path)
    if ret_stat > 0:
        return ret_stat, None
    report = PACKAGES.PackageValidator(checked_path).validation_report
    print('Path {}, struct result is: {}'.format(checked_path,
                                                 report.structure.status.value))
    # for message in report.structure.messages:
    print(report.model_dump_json())

    return ret_stat, report

def _check_path(path: str) -> Tuple[int, Optional[Path]]:
    if not os.path.exists(path):
        # Skip files that don't exist
        print(_format_check_path_message(path, 'does not exist'))
        return 1, None
    if os.path.isfile(path):
        # Check if file is a archive format
        if not PackageHandler.is_archive(path):
            # If not we can't process so report and iterate
            print(_format_check_path_message(path, 'is not an archive file or directory'))
            return 2, None
    return 0, Path(path)

def _format_check_path_message(path: Path, message: str) -> str:
    return 'Processing terminated, path: {} {}.'.format(path, message)

# def _test_case_schema_checks():
if __name__ == '__main__':
    main()
