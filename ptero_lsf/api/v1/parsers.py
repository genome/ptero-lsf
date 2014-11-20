from flask.ext.restful import reqparse


_job_post = reqparse.RequestParser()
_job_post.add_argument('callbacks', type=dict)
_job_post.add_argument('commandLine', type=list, dest='command_line')
_job_post.add_argument('environment', type=dict)
_job_post.add_argument('stdin', type=str)
_job_post.add_argument('umask', type=int)
_job_post.add_argument('user', type=str)
_job_post.add_argument('workingDirectory', type=str, dest='working_directory')
def get_job_post_data():
    data = _job_post.parse_args()
    return data
