from .base import Base
from sqlalchemy import event
from sqlalchemy.util import symbol
from ptero_lsf.implementation import statuses
from sqlalchemy import Column, func
from sqlalchemy import DateTime, ForeignKey, Integer, Interval, Text, Boolean
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import object_session
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import JSON
import celery
import os
import pwd
import string
from ptero_common import nicer_logging


LOG = nicer_logging.getLogger(__name__)


class PreExecFailed(Exception):
    pass


__all__ = ['Job', 'JobStatusHistory']


_TERMINAL_STATUSES = {
    statuses.errored,
    statuses.failed,
    statuses.succeeded,
}


class Job(Base):
    __tablename__ = 'job'

    id = Column(UUID(), primary_key=True)

    command = Column(Text, nullable=False)
    options = Column(JSON)
    rlimits = Column(JSON)

    stdout = Column(Text)
    stderr = Column(Text)

    cwd = Column(Text, nullable=False)
    environment = Column(JSON, default=dict)
    umask = Column(Integer)

    created_at = Column(DateTime(timezone=True), default=func.now(),
                        nullable=False)

    lsf_job_id = Column(Integer, index=True)

    poll_after = Column(DateTime, nullable=True, index=True)
    polling_interval = Column(Interval, nullable=False)

    user = Column(Text, nullable=False, index=True)
    webhooks = Column(JSON, default=lambda: {}, nullable=False)

    awaiting_update = Column(Boolean, default=False, nullable=False,
            index=True)
    failed_update_count = Column(Integer, default=0, nullable=False,
            index=True)

    @property
    def latest_status(self):
        statuses = self.status_history
        if statuses:
            return statuses[-1]

    def set_status(self, status, message=None):
        JobStatusHistory(job=self, status=status, message=message)
        self.trigger_webhook(status)

    def update_status(self, lsf_status_set, message=None):
        current_status = _extract_status(lsf_status_set)

        last_status_obj = self.latest_status
        if last_status_obj.status == current_status:
            if last_status_obj.times_seen is None:
                last_status_obj.times_seen = 2
            else:
                last_status_obj.times_seen += 1
        else:
            lsf_primary_status = _extract_primary_status(lsf_status_set)
            lsf_sorted_statuses = sorted(lsf_status_set)

            JobStatusHistory(job=self, status=current_status,
                             lsf_status_set=lsf_sorted_statuses,
                             lsf_primary_status=lsf_primary_status,
                             message=message)
            self.trigger_webhook(current_status)

    def update_poll_after(self):
        if self.latest_status.status in _TERMINAL_STATUSES:
            self.poll_after = None
        else:
            s = object_session(self)
            now = s.execute(func.now()).first()[0]
            s.query(Job).filter_by(id=self.id).update({
                'poll_after': now + self.polling_interval,
            })

    @property
    def submit_options(self):
        if self.options is not None:
            # lsf gets mad if numProcessors is set but maxNumProcessors isn't
            options = dict(self.options)
            if 'numProcessors' in options and 'maxNumProcessors' not in options:
                options['maxNumProcessors'] = options['numProcessors']
            return options

    def set_cwd(self):
        os.chdir(self.cwd)

    def set_environment(self):
        os.environ.clear()
        os.environ.update(self.environment)

    def set_umask(self):
        if self.umask is not None:
            os.umask(self.umask)

    def translate_output_paths(self):
        if self.stdout is not None:
            self.stdout = self._translate(self.stdout)
        if self.stderr is not None:
            self.stderr = self._translate(self.stderr)

    def _translate(self, path):
        return string.replace(path, '%%JOB_ID%%', self.id)

    @property
    def process_user(self):
        return pwd.getpwuid(os.getuid())[0]

    def set_user_and_groups(self):
        pw_ent = self._get_pw_ent(self.user)

        if self.process_user == 'root':
            self._set_groups(self.user, pw_ent.pw_gid)
            self._set_gid(pw_ent.pw_gid)
            self._set_uid(pw_ent.pw_uid)
        elif self.process_user != self.user:
            raise PreExecFailed("Attempted submit job as invalid user (%s),"
                    " only valid value is (%s)" %
                    (self.user, self.process_user))

    def _get_pw_ent(self, user):
        try:
            pw_ent = pwd.getpwnam(user)
        except KeyError as e:
            raise PreExecFailed(e.message)
        return pw_ent

    def _set_groups(self, user, gid):
        try:
            os.initgroups(user, gid)
        except OSError as e:
            raise PreExecFailed('Failed to initgroups: ' + e.strerror)

    def _set_gid(self, gid):
        try:
            os.setregid(gid, gid)
        except OSError as e:
            raise PreExecFailed('Failed to setregid: ' + e.strerror)

    def _set_uid(self, uid):
        try:
            os.setreuid(uid, uid)
        except OSError as e:
            raise PreExecFailed('Failed to setreuid: ' + e.strerror)

    @property
    def as_dict(self):
        result = {
            'command': self.command,
            'cwd': self.cwd,
            'environment': self.environment,
            'jobId': self.id,
            'pollingInterval': self.polling_interval.seconds,
            'status': self.latest_status.status,
            'statusHistory': [h.as_dict for h in self.status_history],
            'user': self.user,
            'webhooks': self.webhooks,
            'stdout': self.stdout,
            'stderr': self.stderr,
        }

        if self.poll_after is not None:
            result['pollAfter'] = self.poll_after.isoformat()

        if self.umask is not None:
            result['umask'] = oct(self.umask)

        self._conditional_add(result, 'options', 'options')
        self._conditional_add(result, 'rlimits', 'rLimits')
        self._conditional_add(result, 'lsf_job_id', 'lsfJobId')
#        self._conditional_add(result, 'stdout', 'stdout')
#        self._conditional_add(result, 'stderr', 'stderr')

        return result

    def _conditional_add(self, result, prop, name):
        value = getattr(self, prop)
        if value is not None:
            result[name] = value

    def trigger_webhook(self, webhook_name):
        if webhook_name:
            webhooks = self.webhooks if self.webhooks is not None else {}

            urls = webhooks.get(webhook_name, [])
            if not isinstance(urls, list):
                urls = [urls]

            for url in urls:
                LOG.info('Webhook: "%s" for job %s -- %s',
                        webhook_name, self.id, url,
                        extra={'jobId': self.id})
                celery.current_app.tasks['ptero_common.celery.http.HTTP'
                        ].delay('POST', url, **self.as_dict)


_STATUS_MAP = {
    'DONE': statuses.succeeded,
    'EXIT': statuses.failed,
    'PEND': statuses.scheduled,
    'PSUSP': statuses.suspended,
    'RUN': statuses.running,
    'SSUSP': statuses.suspended,
    'USUSP': statuses.suspended,
    'WAIT': statuses.waiting,
}


def _extract_status(lsf_status_set):
    for lsf_status, status in _STATUS_MAP.iteritems():
        if lsf_status in lsf_status_set:
            return status

    return 'UNKNOWN'


def _extract_primary_status(lsf_status_set):
    return lsf_status_set[0]


class JobStatusHistory(Base):
    __tablename__ = 'job_status_history'

    id = Column(Integer, primary_key=True)
    job_id = Column(UUID(), ForeignKey(Job.id, ondelete='CASCADE'),
            nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(),
                       nullable=False)
    last_updated = Column(DateTime(timezone=True), nullable=True,
            onupdate=func.now())
    times_seen = Column(Integer, nullable=True)

    status = Column(Text, index=True, nullable=False)

    lsf_primary_status = Column(Text, index=True)
    lsf_status_set = Column(JSON)

    message = Column(Text)

    job = relationship(Job, backref=backref('status_history',
        order_by=timestamp,
        passive_deletes='all'))

    @property
    def as_dict(self):
        result = {
            'status': self.status,
        }

        if self.timestamp is not None:
            result['timestamp'] = self.timestamp.isoformat()

        if self.message is not None:
            result['message'] = self.message

        if self.lsf_primary_status is not None:
            result['lsfPrimaryStatus'] = self.lsf_primary_status

        if self.lsf_status_set is not None:
            result['lsfStatusSet'] = self.lsf_status_set

        if self.last_updated is not None:
            result['lastUpdated'] = self.last_updated.isoformat()

        if self.times_seen is not None:
            result['timesSeen'] = self.times_seen

        return result


@event.listens_for(Job.stderr, 'set')
def receive_job_stderr(*args, **kwargs):
    return set_only_once(*args, **kwargs)


@event.listens_for(Job.stdout, 'set')
def receive_job_stdout(*args, **kwargs):
    return set_only_once(*args, **kwargs)


def set_only_once(target, new_value, old_value, initiator):
    if old_value == new_value:
        return

    if old_value not in [None, symbol('NEVER_SET'), symbol('NO_VALUE')]:
        raise AttributeError("Attempted to set an immutable attribute")
