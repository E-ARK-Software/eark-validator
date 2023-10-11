#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup for the E-ARK Python Validation Suite."""

import codecs
import os
import re

from setuptools import setup, find_packages

def read(*parts):
    """ Read a file and return the contents. """
    path = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(path, encoding='utf-8') as fobj:
        return fobj.read()

def find_version(version_id, *file_paths):
    """Parse the module version, matching version_id from any found in file_paths."""
    version_file = read(*file_paths)
    version_match = re.search(r"^{} = ['\"]([^'\"]*)['\"]".format(version_id), version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')

INSTALL_REQUIRES = [
    'setuptools',
    'lxml',
    'importlib_resources',
]

SETUP_REQUIRES = [
    'pytest-runner',
]

TEST_DEPS = [
    'pre-commit',
    'pytest',
    'pylint',
    'pytest-cov',
    'pre-commit',
]

EXTRAS = {
    'testing': TEST_DEPS,
    'setup': SETUP_REQUIRES,
}

with open('README.md', 'r') as README:
    README_TEXT = README.read()

setup(name='eark-ip-validation',
      packages=find_packages(),
      version=find_version('__version__', 'ip_validation', '__init__.py'),
      description='E-ARK Python Information Package validation library.',
      long_description=README_TEXT,
      long_description_content_type='text/markdown',
      author='Carl Wilson',
      author_email='carl@openpreservation.org',
      maintainer='Carl Wilson',
      maintainer_email='carl@openpreservation.org',
      url='https://github.com/E-ARK-Software/py-e-ark-ip-validator',
      download_url='https://github.com/E-ARK-Software/py-e-ark-ip-validator/archive/' \
        + find_version('__version__', 'ip_validation', '__init__.py') + '.tar.gz',
      package_data={'ip_validation': ['*.*', 'cli/resources/*.*', 'xml/resources/schema/*.*', 'xml/resources/profiles/*.*']},
      license='Apache License 2.0',
      entry_points={'console_scripts': [
          'ip-check = ip_validation.cli.app:main',
      ]},
      classifiers=[
          'Intended Audience :: Archivists',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      install_requires=INSTALL_REQUIRES,
      setup_requires=SETUP_REQUIRES,
      tests_require=TEST_DEPS,
      extras_require=EXTRAS,
      test_suite='tests',
     )
