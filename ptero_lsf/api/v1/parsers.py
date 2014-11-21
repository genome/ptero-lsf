from flask.ext.restful import reqparse


_job_post = reqparse.RequestParser()
_job_post.add_argument('command')
def get_job_post_data():
    data = _job_post.parse_args()
    return data
