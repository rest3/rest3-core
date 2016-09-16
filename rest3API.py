from flask import Flask, request, redirect, flash, jsonify, render_template, send_from_directory

import requests
import os
import logging

from flask_cors import CORS
from werkzeug.utils import secure_filename
import fileops
from flask_restplus import Api, Resource

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

app = Flask(__name__)
CORS(app, send_wildcard=True)

api = Api(app, version='1.0', title='rest3', description='An OSS Container Object Store')
ns = api.namespace('rest3', description='An OSS Container Object Store')

UPLOAD_FOLDER = '/root/ierepo/staging/'
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md'}

requests.packages.urllib3.disable_warnings()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@ns.route('/api/v1/download/<bucket>/<file>', endpoint='download file')
class Download(Resource):
    def get(self, bucket, file):
        return send_from_directory(app.config['UPLOAD_FOLDER'] + bucket, file)


@ns.route('/api/v1/buckets', methods=['GET', 'POST'], endpoint='bucket list')
class ListBuckets(Resource):
    def get(self):
        return jsonify(buckets=fileops.getbuckets())


@ns.route('/api/v1/buckets/<bucket>', methods=['GET', 'POST', 'PUT', 'DELETE'], endpoint='bucket actions')
class BucketActions(Resource):
    def get(self, bucket):
        return jsonify(bucket=fileops.getbucketinfo(bucket))

    def post(self, bucket):
        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], bucket)):
            os.makedirs(app.config['UPLOAD_FOLDER'] + bucket)
            fileops.newbucket(bucket)

    def put(self):
        return jsonify(bucket=fileops.updateobjectmetadata())

    def delete(self, bucket):
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], bucket)):
            # delete bucket
            fileops.deletebucket(bucket)
            os.removedirs(app.config['UPLOAD_FOLDER'] + bucket)


@ns.route('/api/v1/buckets/<bucket>/<object_name>', methods=['POST', 'DELETE'], endpoint='object actions')
class ObjectActions(Resource):
    def post(self, bucket, object_name):
        body = request.get_json(force=True)
        fileops.addobjectmetadata(bucket, object_name, body['metadata'])
        return 'OK'

    def delete(self, bucket, object_name):
        # delete object
        fileops.removeobjectmetadata(bucket, object_name)
        os.remove(app.config['UPLOAD_FOLDER'] + bucket + '/' + object_name)
        return 'OK'


@ns.route('/api/v1/upload', methods=['GET', 'POST'], endpoint='upload')
class NewFile(Resource):
    def get(self):
        return 'OK'

    def post(self):
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        _file = request.files['file']
        if _file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if _file and allowed_file(_file.filename):
            filename = secure_filename(_file.filename)
            bucket = request.form['bucket']
            _file.save(os.path.join(app.config['UPLOAD_FOLDER'] + request.form['bucket'], filename))
            fileops.addobjectmetadata(bucket, filename, '')
            # TODO additional processing here
            return 'OK'  # redirect('/' + request.form['bucket'])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
