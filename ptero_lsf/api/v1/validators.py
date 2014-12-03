from flask import request
import json
import jsonschema
import pkg_resources


def _load_schema(schema_name):
    return json.load(pkg_resources.resource_stream('ptero_lsf',
        _schema_path(schema_name)))


_BASE_PATH = '/'.join(__package__.split('.')[1:])
def _schema_path(schema_name):
    return '%s/schemas/%s.json' % (_BASE_PATH, schema_name)


_POST_JOB_SCHEMA = _load_schema('post_job')
def get_job_post_data():
    data = request.json
    jsonschema.validate(data, _POST_JOB_SCHEMA)
    return data
