import celery
import logging
import os
import subprocess

__all__ = ['ShellCommandTask']


class ShellCommandTask(celery.Task):
    def run(self, command_line, environment=None, logging_configuration=None,
            stderr=None, stdin=None, stdout=None, callbacks=None):
        stdout_logger, stderr_logger = _get_data_loggers(logging_configuration)
        self.callback('begun', callbacks)

        p = subprocess.Popen(command_line, env=environment, close_fds=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # XXX We cannot use communicate for real, because communicate buffers
        # the data in memory until the process ends.
        stdout_data, stderr_data = p.communicate()
        stdout_logger.log_data(stdout_data)
        stderr_logger.log_data(stderr_data)

        exit_code = p.wait()

        if exit_code == 0:
            self.callback('succeeded', callbacks)
        else:
            self.callback('failed', callbacks)

        return {'exit_code': exit_code}

    def callback(self, status, callbacks):
        if callbacks is None:
            return

        if status in callbacks:
            task = self._get_http_task()
            task.delay(callbacks[status], status)

    def _get_http_task(self):
        return celery.current_app.tasks[
'ptero_shell_command_fork.implementation.celery_tasks.http_callback.HTTPCallbackTask'
        ]


class NullLogger(object):
    def log_data(self, data):
        pass

class DataLogger(object):
    def __init__(self, loggers):
        self.loggers = loggers
        self.buf = ''

    def log_data(self, data):
        lines = data.split('\n')
        lines[0] = self.buf + lines[0]
        for line in lines[:-1]:
            for logger in self.loggers:
                logger.info(line)
        self.buf = lines[-1]


def _get_data_loggers(configuration):
    if configuration is None:
        return NullLogger(), NullLogger()

    if 'stderr' in configuration:
        stderr_logger = DataLogger(
                _get_low_level_loggers(configuration['stderr']))
    else:
        stderr_logger = NullLogger()

    if 'stdout' in configuration:
        stdout_logger = DataLogger(
                _get_low_level_loggers(configuration['stdout']))
    else:
        stdout_logger = NullLogger()

    return stdout_logger, stderr_logger


def _get_file_logger(path=None, format_string='%(message)s', type=None):
    logger = logging.Logger(name='something')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(path)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    handler.setFormatter(logging.Formatter(format_string))

    return logger

_LOGGER_FACTORIES = {
    'file': _get_file_logger,
}
def _get_low_level_loggers(configurations):
    result = []
    for config in configurations:
        result.append(_LOGGER_FACTORIES[config['type']](**config))

    return result
