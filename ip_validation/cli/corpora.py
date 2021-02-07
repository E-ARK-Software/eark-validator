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
        E-ARK Test Corpus processing
"""
import argparse
from datetime import datetime
import os.path
import sys

from jinja2 import Environment, PackageLoader
from ip_validation.cli.testcases import TestCase, DEFAULT_NAME
from ip_validation.infopacks.specification import Specification
__version__ = "0.1.0"

defaults = {
    'description': """E-ARK Test Case validation (tc-check).
tc-check is a command-line tool to run test across corpora.""",
    'epilog': """
DILCIS Board (http://dilcis.eu)
See LICENSE for license information.
GitHub: https://github.com/E-ARK-Software/py-rest-ip-validator
Author: Carl Wilson (OPF), 2020
Maintainer: Carl Wilson (OPF), 2020"""
}

class Corpus():
    """
    Encapsulates a test corpus of E-ARK information packages.
    """
    def __init__(self, name, root, case_paths=None):
        self._name = name
        self._root = root
        self._cases = {} if case_paths is None else self._load_cases(case_paths)

    @property
    def name(self):
        """Return the corpus name."""
        return self._name

    @property
    def root(self):
        """Return the corpus' root directory path."""
        return self._root

    @property
    def cases(self):
        """Generator to return test cases in a iterable form."""
        for case in self._cases.values():
            yield case

    @property
    def case_count(self):
        """Return the number of test cases in the corpus."""
        return len(self._cases)

    @property
    def rule_count(self):
        """Return the total number of validation rules in the corpus."""
        count = 0
        for case in self.cases:
            count+=len(case.rules)
        return count

    @property
    def package_count(self):
        """Return the total number of test packages in the corpus."""
        count = 0
        for case in self.cases:
            count+=case.package_count
        return count

    @property
    def missing_package_count(self):
        """Return the total number of test packages in the corpus."""
        count = 0
        for case in self.cases:
            count+=case.missing_package_count
        return count

    def case_by_id(self, case_id):
        """Return an individual test case by ID."""
        case = self._cases.get(case_id, None)
        return case

    def __str__(self):
        return "name:" + self.name + ", root:" + self.root + ", cases:" + str(self.case_count) + \
            ", rules:" + str(self.rule_count) + ", packages:" + str(self.package_count)

    @classmethod
    def _load_cases(cls, case_paths):
        cases = {}
        for path in case_paths:
            case = TestCase.from_xml_file(os.path.join(path, DEFAULT_NAME))
            cases[case.case_id.requirement_id] = case
        return cases

    @classmethod
    def from_root(cls, root, name):
        """Create a new corpus instance from a root directory."""
        if not os.path.exists(root) or not os.path.isdir(root):
            return None
        cases = _get_test_cases(root)
        return cls(name, root, cases)

ROOT = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(ROOT, 'templates')
env = Environment( loader = PackageLoader('ip_validation.cli') )

def corpus_html(root, corpus, specification):
    """Write an HTML file summarising a corpus."""
    template = env.get_template('corpus.html')
    template.globals['now'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    _mkdirs(root)
    with open(os.path.join(root, 'index.html'), 'w') as filehand:
        filehand.write(template.render(
            corpus = corpus,
            specification = specification,
        ))

def case_html(root, case):
    """Write an HTML file summarising a test case."""
    if case is None or case.case_id is None or case.case_id.requirement_id is None:
        return
    template = env.get_template('case.html')
    out_dir = os.path.join(root, case.case_id.requirement_id)
    _mkdirs(out_dir)
    with open(os.path.join(out_dir, 'index.html'), 'w') as filehand:
        filehand.write(template.render(
            case = case,
        ))
    for rule in case.rules:
        for package in rule.packages:
            package_html(out_dir, case, rule, package)

def package_html(root, case, rule, package):
    """Write an HTML file summarising a package."""
    template = env.get_template('package.html')
    out_dir = os.path.join(root, package.name)
    _mkdirs(out_dir)
    with open(os.path.join(out_dir, 'index.html'), 'w') as filehand:
        filehand.write(template.render(
            case = case,
            rule = rule,
            package = package,
        ))

def _mkdirs(_dir):
    try:
        os.makedirs(_dir)
    except FileExistsError:
        # directory already exists
        pass


def _get_test_cases(root):
    cases = []
    for rootdir, subdirs, files in os.walk(root):
        for file in files:
            if file == DEFAULT_NAME:
                cases.append(rootdir)
        for subdir in subdirs:
            cases+=(_get_test_cases(subdir))
    return cases

# Create PARSER
PARSER = argparse.ArgumentParser(description=defaults['description'], epilog=defaults['epilog'])

def parse_command_line():
    """Parse command line arguments."""
    # Add arguments
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
    _exit = 0
    # Get input from command line
    args = parse_command_line()
    # If no target files or folders specified then print usage and exit
    if not args.files:
        PARSER.print_help()

    # Iterate the file arguments
    specification = Specification.from_xml_file()
    for file_arg in args.files:
        corpus = Corpus.from_root(file_arg, 'CSIP')
        corpus_html('results', corpus, specification)
        for case in corpus.cases:
            case_html('results', case)
    sys.exit(_exit)

if __name__ == "__main__":
    main()
