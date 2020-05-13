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
""" Flask application routes for E-ARK Python IP Validator. """
import logging
import os.path
import tarfile
import tempfile
import zipfile

import lxml.etree as ET

from flask import render_template, request, redirect, url_for
from flask_negotiate import produces
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Unauthorized, InternalServerError

from eatb.metadata.mets import MetsValidation

from .webapp import APP, __version__
from .rules import ValidationProfile, TestResult

ROUTES = True

JSON_MIME = 'application/json'
PDF_MIME = 'application/pdf'
XML_MIME = 'text/xml'
@APP.route("/")
def home():
    """Application home page."""
    return render_template('home.html')

@APP.route("/api/report/<report_id>/")
@produces(JSON_MIME, XML_MIME)
def full_report():
    """Download a full file system analysis report."""
    if _request_wants_json():
        logging.debug("JSON file report for %s:%s")
    logging.debug("XML file report for %s:%s")

@APP.route("/specifications/")
def get_specifications():
    """Get """
    return render_template('specifications.html')

@APP.route("/specifications/<string:spec_name>/")
def get_specification(spec_name):
    """Get """
    return render_template('blobstore.html')

@APP.route("/validate/<string:digest>/", endpoint="validate")
def validate(digest):
    """Display validation results."""
    to_validate = os.path.join(APP.config['UPLOAD_FOLDER'], digest)
    with tempfile.TemporaryDirectory() as tmpdirname:
        if zipfile.is_zipfile(to_validate):
            zip_ip = zipfile.ZipFile(to_validate)
            zip_ip.extractall(path=tmpdirname)
        elif tarfile.is_tarfile(to_validate):
            tar_ip = tarfile.open(to_validate)
            tar_ip.extractall(path=tmpdirname)
        else:
            raise BadRequest("Invalid Package Format")
        root_entries = os.listdir(tmpdirname)
        if len(root_entries) != 1:
            return "Invalid Package without a single root directory."
        package_root = os.path.join(tmpdirname, root_entries[0])
        validator = MetsValidation.MetsValidation(tmpdirname)
        mets_path = os.path.join(package_root, 'METS.xml')
        schema_result = validator.validate_mets(mets_path)
        schema_errors = []
        for error in validator.validation_errors:
            schema_errors.append(str(error))

        profile = ValidationProfile()
        profile.validate(mets_path)
        errors = []

        for sect in ["root", "hdr", "amd", "dmd", "file", "structmap"]:
            if not profile.get_result(sect):
                report = profile.rulesets[sect].get_report()
                xml_report = ET.XML(bytes(report))

                rule = None
                for ele in xml_report.iter():
                    if ele.tag == '{http://purl.oclc.org/dsdl/svrl}fired-rule':
                        rule = ele
                        print(format(rule))
                    elif ele.tag == '{http://purl.oclc.org/dsdl/svrl}failed-assert':
                        print(format(rule))
                        print(format(ele))
                        errors.append(TestResult.from_element(rule, ele))
        return render_template('validate.html', schema_result=schema_result,
                               schema_errors=schema_errors,
                               results=profile.get_results(), errors=errors)
    raise InternalServerError("Failed to process package")

@APP.route("/api/validate/", methods=['POST'])
def upload():
    """POST method to valdiate an information package."""
    # check if the post request has the file part

    if not request.files['package'] or not request.form["digest"]:
        logging.debug('No file part %s', request.files)
        raise BadRequest('No file part, or digest')
    uploaded = request.files['package']
    digest = request.form["digest"]
    if uploaded.filename == '':
        logging.debug('No selected file')
        raise BadRequest('No selected file')
    if uploaded and _allowed_file(uploaded.filename):
        logging.debug("Digest: %s", digest)
        filename = request.form["digest"]
        dest_path = os.path.join(APP.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(dest_path):
            uploaded.save(dest_path)
        logging.debug("File upload successful: %s", filename)
        return redirect(url_for('validate', digest=digest))
    raise BadRequest("File type upload not allowed")

@APP.route("/about/")
def about():
    """Show the application about and config page"""
    return render_template('about.html', config=APP.config, version=__version__)

@APP.errorhandler(BadRequest)
def bad_request_handler(bad_request):
    """Basic bad request handler."""
    return render_template('except.html',
                           http_excep=bad_request,
                           message='bad request {}'.format(str(bad_request)),
                           http_code=403,
                           http_error="Bad Request")

@APP.errorhandler(NotFound)
def not_found_handler(not_found):
    """Basic not found request handler."""
    return render_template('except.html',
                           http_excep=not_found,
                           message='Not resource found at this URL.',
                           http_code=404,
                           http_error="Not Found")

@APP.errorhandler(Forbidden)
def forbidden_handler(forbidden):
    """Basic not found request handler."""
    return render_template('except.html',
                           http_excep=forbidden,
                           message='You\'re forbidden to access this resource.',
                           http_code=403,
                           http_error="Forbidden")

@APP.errorhandler(Unauthorized)
def unauth_handler(unauthorized):
    """Basic not found request handler."""
    return render_template('except.html',
                           http_excep=unauthorized,
                           message='It appears there are no S3 credentials ' +\
                                   'available to the application',
                           http_code=401,
                           http_error="Unauthorized")

@APP.errorhandler(InternalServerError)
def servererr_handler(servererr):
    """Basic not found request handler."""
    return render_template('except.html',
                           http_excep=servererr,
                           message='It appears there are no S3 credentials ' +\
                                   'available to the application',
                           http_code=500,
                           http_error="Internal Server Error")


@APP.teardown_appcontext
def shutdown_session(exception=None):
    """Tear down the database session."""
    if exception:
        logging.warning("Shutting down database session with exception.")

def _request_wants_json():
    best = request.accept_mimetypes \
        .best_match([JSON_MIME, PDF_MIME])
    return best == JSON_MIME and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes[PDF_MIME]

def _request_wants_xml():
    best = request.accept_mimetypes \
        .best_match([XML_MIME, PDF_MIME])
    return best == XML_MIME and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes[PDF_MIME]

def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in APP.config['ALLOWED_EXTENSIONS']

if __name__ == "__main__":
    APP.run(host='0.0.0.0', threaded=True)
