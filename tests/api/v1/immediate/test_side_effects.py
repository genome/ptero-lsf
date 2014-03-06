from .base import ImmediateAPITest
import tempfile


class TestJobSideEffects(ImmediateAPITest):
    def test_environment_set_for_job(self):
        environment = {
            'FOO': 'bar',
        }
        output_file = tempfile.NamedTemporaryFile()

        post_data = {
            'command_line': ['/usr/bin/env'], #, '>>', output_file.name],
            'environment': environment,
            'stdout': output_file.name,
        }

        self.post('/v1/jobs', post_data)

        actual_environment = _extract_environment_dict(output_file)
        self.assertEqual(environment, actual_environment)


def _extract_environment_dict(file_object):
    result = {}
    for line in file_object:
        key, value = line.split('=')
        result[key] = value.strip('\n')
    return result
