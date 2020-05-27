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
"""Configuration for E-ARK validation Flask app."""
import os.path
import tempfile

from flask_debugtoolbar import DebugToolbarExtension

from .const import ENV_CONF_PROFILE, ENV_CONF_FILE

HOST = 'localhost'

TEMP = tempfile.gettempdir()
HOME = os.path.expanduser('~')
LOG_ROOT = TEMP
UPLOADS_TEMP = os.path.join(TEMP, 'ip-uploads')
class BaseConfig():# pylint: disable-msg=R0903
    """Base / default config, no debug logging and short log format."""
    NAME = 'Default'
    HOST = HOST
    DEBUG = False
    TESTING = False
    LOG_FORMAT = '[%(filename)-15s:%(lineno)-5d] %(message)s'
    LOG_FILE = os.path.join(LOG_ROOT, 'eark-pyip-validation.log')
    SECRET_KEY = 'a5c020ced05af9ad3aacc6bba41beb5c7b6f750b846dadad'
    EARKVAL_ROOT = TEMP
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024
    UPLOAD_FOLDER = UPLOADS_TEMP
    ALLOWED_EXTENSIONS = {'zip', 'tar', 'gz', 'gzip'}

class DevConfig(BaseConfig):# pylint: disable-msg=R0903
    """Developer level config, with debug logging and long log format."""
    NAME = 'Development'
    DEBUG = True
    TESTING = True
    LOG_FORMAT = '[%(levelname)-8s %(filename)-15s:%(lineno)-5d %(funcName)-30s] %(message)s'

class TestConfig(BaseConfig):# pylint: disable-msg=R0903
    """Developer level config, with debug logging and long log format."""
    NAME = 'Testing'

CONFIGS = {
    "dev": 'ip_validation.config.DevConfig',
    "default": 'ip_validation.config.BaseConfig',
    "test": 'ip_validation.config.TestConfig'
}

def configure_app(app, profile_name='dev'):
    """Grabs the environment variable for app config or defaults to dev."""
    config_name = os.getenv(ENV_CONF_PROFILE, profile_name)
    app.config.from_object(CONFIGS[config_name])
    if os.getenv(ENV_CONF_FILE):
        app.config.from_envvar(ENV_CONF_FILE)
    if not os.path.exists(UPLOADS_TEMP):
        os.makedirs(UPLOADS_TEMP)
    # DebugToolbarExtension(app)
