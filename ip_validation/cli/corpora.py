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
from pathlib import Path
import sys

from git import Repo
from jinja2 import Environment, PackageLoader

from ip_validation.cli.testcases import TestCase, DEFAULT_NAME, GitTestCase
from ip_validation.infopacks.specification import SPECIFICATIONS
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
    def __init__(self, name, root, cases=None):
        self._name = name
        self._root = root
        self._cases = {} if cases is None else self._load_cases(cases)

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
    def _load_cases(cls, cases):
        cases_dict = {}
        for case in cases:
            cases_dict[case.case_id.requirement_id] = case
        return cases_dict

    @classmethod
    def from_root(cls, root, name):
        """Create a new corpus instance from a root directory."""
        if not os.path.exists(root) or not os.path.isdir(root):
            return None
        cases = _get_test_cases(root)
        return cls(name, root, cases)

class Corpora():
    """Encapsulates the full set of E-ARK corpora derived from the contents of
    the git repository."""
    def __init__(self, git_path, corpora, skipped=None):
        self._git_path = git_path
        self._corpora = corpora
        self._skipped = skipped if skipped else []

    @property
    def git_path(self):
        """Return the git repository path."""
        return self._git_path

    @property
    def corpora(self):
        """Return the full copora dictionary."""
        return self._corpora

    def corpus_by_key(self, name):
        """Return a corpus by name."""
        return self._corpora[name]

    @property
    def skipped(self):
        """Return the list of skipped branches."""
        return self._skipped

    @classmethod
    def from_git_repo(cls, git_path):
        """Create all corpus instances from a git repository root."""
        # Open the passed path as if it were a git repo
        if not os.path.exists(git_path) or not os.path.isdir(git_path):
            raise ValueError('Parameter {} must be an existing directory.'.format(git_path))
        repo = Repo(git_path)
        # empty list to store the skipped branches
        skipped = []
        # Empty dictionary for the corpora
        case_lookup = {}
        for key in SPECIFICATIONS:
            # Empty list for each specification key
            case_lookup[key] = []
        # Loop through the remote branches
        for ref in repo.remote().refs:
            # Get the test case for this ref
            test_case, message = cls.test_case_from_ref(ref)
            if test_case is None:
                skipped.append('{}:{}'.format(ref.name, message))
                continue
            try:
                case_lookup[test_case.case_id.specification].append(test_case)
            except AttributeError:
                print('Exception: {}'.format(test_case))
        return cls.build_corpora(git_path, case_lookup)

    @classmethod
    def build_corpora(cls, git_path, cases):
        """Return a corpus dictionary populated with passed cases."""
        corpora = {}
        for item, value in cases.items():
            corpora[item] = Corpus(item, git_path, value)
        return corpora

    @classmethod
    def test_case_from_ref(cls, ref):
        """Return the test case for a particular git reference."""
        name_parts = ref.name.split('/')
        # The branch name should be 4 parts origin/<corpus>/<section>/<reqID>
        # If the path isn't 4 parts or the second element is not an recognised
        # corpus id then return nothing.
        if (len(name_parts) != 4) | (name_parts[1].upper() not in SPECIFICATIONS):
            return None, 'Invalid branch name.'

        # Iterate the paths of the blobs found for this commit tree
        for path in _list_tree_paths(ref.commit.tree):

            # get lower case path elements as a list
            path_parts = str(path).lower().split('/')

            # if the branch name requirement id is found in the path
            # AND the element name (without path, basename) is testCase.xml
            if (name_parts[3].lower() in path_parts) & (path.name == DEFAULT_NAME):
                # test case match, return the results of parsing
                case, message = cls.test_case_from_tree_path(ref.commit.tree, path)
                return GitTestCase(ref, path, case), message

        # Never found a matching test case
        return None, 'No test case found for {}.'.format(ref.name)

    @classmethod
    def test_case_from_tree_path(cls, tree, path):
        """Return the test case parsed from the blob defined by tree and path params."""
        # get the blob from commit tree and path
        test_case_blob = tree / str(path)
        try:
            # Return the test case and it's path
            _tc = TestCase.from_xml_string(test_case_blob.data_stream.read())
            if not _tc.valid:
                return None, 'Test case XML failed schema validation for {}.'.format(str(path))
            return _tc, str(path)
        except ValueError:
            # Bad test case XML.
            return None, 'Badly formed test case XML in file {}.'.format(str(path))

def _list_tree_paths(root, path=Path('.')):
    for blob in root.blobs:
        yield path / blob.name
    for tree in root.trees:
        yield from _list_tree_paths(tree, path / tree.name)

ROOT = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(ROOT, 'templates')
env = Environment( loader = PackageLoader('ip_validation.cli') )

def app_html(root, specifications, corpora):
    """Write an HTML file home page."""
    template = env.get_template('home.html')
    _mkdirs(root)
    with open(os.path.join(root, 'index.html'), 'w') as filehand:
        filehand.write(template.render(
            specifications=specifications,
            corpora=corpora
        ))

def corpus_html(root, corpus, specification):
    """Write an HTML file summarising a corpus."""
    if (root is None) | (corpus is None) | (specification is None):
        return
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

    corpora = {}
    for file_arg in args.files:
        corpora = Corpora.from_git_repo(file_arg)
        for key in SPECIFICATIONS:
            print('spec key: {}'.format(key))
            corpus = corpora[key]
            print(str(corpus))
            if corpus:
                corpus_html(os.path.join('results', key), corpus, SPECIFICATIONS[key])
                for case in corpus.cases:
                    case_html(os.path.join('results', key), case)
                corpora[key] = corpus

    app_html('results', SPECIFICATIONS, corpora)
    sys.exit(_exit)

if __name__ == "__main__":
    main()
