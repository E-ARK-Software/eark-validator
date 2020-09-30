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

from flask import jsonify, render_template, request, redirect, url_for
from flask_negotiate import produces
from werkzeug.exceptions import BadRequest, Forbidden, NotFound, Unauthorized, InternalServerError

from ip_validation.infopacks.mets import MetsValidator

from ip_validation.webapp import APP, __version__
from ip_validation.infopacks.rules import ValidationProfile
import ip_validation.infopacks.information_package as IP
import ip_validation.utils as UTILS

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
    # Get the validation path ready
    to_validate = os.path.join(APP.config['UPLOAD_FOLDER'], digest)
    # Validate package structure
    struct_details = IP.validate_package_structure(to_validate)
    # Schema and schematron validation to be factored out.
    # initialise schema and schematron validation structures
    schema_result = None
    prof_results = {}
    schema_errors = []
    # Schematron validation profile
    profile = ValidationProfile()
    # IF package is well formed then we can validate it.
    if struct_details.package_status == IP.PackageStatus.WellFormed:
        # Schema based METS validation first
        validator = MetsValidator(struct_details.path)
        mets_path = os.path.join(struct_details.path, 'METS.xml')
        schema_result = validator.validate_mets(mets_path)
        # Now grab any errors
        schema_errors = validator.validation_errors
        if schema_result is True:
            profile.validate(mets_path)
            prof_results = profile.get_results()

    return render_template('validate.html', details=struct_details, schema_result=schema_result,
                           schema_errors=schema_errors, prof_names=ValidationProfile.NAMES,
                           schematron_result=profile.is_valid, profile_results=prof_results)

@APP.route("/api/validate/", methods=['POST'])
def upload_redirect():
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

@APP.route("/api/ip/package/", methods=['POST'])
def upload():
    """POST method to valdiate an information package."""
    # check if the post request has the file part
    if not request.files['package'] or not request.form["digest"]:
        logging.debug('No file part %s', request.files)
        return {'message' : 'No file part, or digest'}, 403
    uploaded = request.files['package']
    digest = request.form["digest"]
    if uploaded.filename == '':
        logging.debug('No selected file')
        return {'message' : 'No selected file'}, 403
    if uploaded and _allowed_file(uploaded.filename):
        logging.debug("Digest: %s", digest)
        filename = request.form["digest"]
        dest_path = os.path.join(APP.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(dest_path):
            uploaded.save(dest_path)
        sha1_hash = UTILS.sha1(dest_path)
        if not sha1_hash == digest:
            return {'message' : 'Digest mismatch, calculated {}, POSTED {}'.format(sha1_hash,
                                                                                   digest)}, 403
        logging.debug("File upload successful: %s", uploaded.filename)
        return jsonify(sha1=digest,
                       validation_url="https://{}/api/ip/validation/{}/".format(request.host,
                                                                                digest))
    return {'message' : 'File type upload not allowed'}, 403

@APP.route("/api/ip/validation/<string:digest>/")
def api_validate(digest):
    """Display validation results."""
    # Get the validation path ready
    to_validate = os.path.join(APP.config['UPLOAD_FOLDER'], digest)
    # Validate package structure
    struct_details = IP.validate_package_structure(to_validate)
    # Schema and schematron validation to be factored out.
    # initialise schema and schematron validation structures
    schema_valid = None
    schema_messages = []
    profile_valid = None
    profile_warnings = []
    profile_errors = []
    # Schematron validation profile
    profile = ValidationProfile()
    # IF package is well formed then we can validate it.
    if struct_details.package_status == IP.PackageStatus.WellFormed:
        # Schema based METS validation first
        validator = MetsValidator(struct_details.path)
        mets_path = os.path.join(struct_details.path, 'METS.xml')
        schema_valid = validator.validate_mets(mets_path)
        # Now grab any errors
        schema_errors = validator.validation_errors
        if schema_valid is True:
            profile.validate(mets_path)
            profile_valid = profile.is_valid
            for name in ValidationProfile.SECTIONS:
                report = profile.get_result(name)
                for failure in report.failures:
                    profile_errors.append(failure.to_Json())
                for warning in report.warnings:
                    profile_warnings.append(warning.to_Json())
        else:
            for _err in schema_errors:
                schema_messages.append(_err.msg)
    return jsonify(schema_valid=schema_valid, schema_errors=schema_messages,
                   metadata_valid=profile_valid, profile_warnings=profile_warnings,
                   profile_errors=profile_errors)

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
