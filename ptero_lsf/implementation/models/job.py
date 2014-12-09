from .base import Base
from json_type import JSON
from sqlalchemy import Column, func
from sqlalchemy import DateTime, ForeignKey, Integer, Interval, Text
from sqlalchemy.orm import backref, relationship
from sqlalchemy.orm import object_session
import celery
import datetime
import lsf


__all__ = ['Job']


_TERMINAL_STATUSES = {
    'ERRORED',
    'FAILED',
    'SUCCEEDED',
}
_WEBHOOK_TO_TRIGGER = {
    'ERRORED': 'error',
    'FAILED': 'failure',
    'RUNNING': 'running',
    'SCHEDULED': 'scheduled',
    'SUCCEEDED': 'success',
    'SUSPENDED': 'suspended',
}


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)

    command = Column(Text, nullable=False)
    options = Column(JSON)
    rlimits = Column(JSON)

    cwd = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), default=func.now(),
                        nullable=False)

    lsf_job_id = Column(Integer, index=True)

    poll_after = Column(DateTime, nullable=True, index=True)
    polling_interval = Column(Interval, nullable=False)

    webhooks = Column(JSON, default=lambda: {}, nullable=False)

    @property
    def latest_status(self):
        statuses = self.status_history
        if statuses:
            return statuses[-1]

    def set_status(self, status):
        JobStatusHistory(job=self, status=status)

    def update_status(self, lsf_status_set):
        current_status = _extract_status(lsf_status_set)
        lsf_primary_status = _extract_primary_status(lsf_status_set)
        lsf_sorted_statuses = sorted(lsf_status_set)

        JobStatusHistory(job=self, status=current_status,
                         lsf_status_set=lsf_sorted_statuses,
                         lsf_primary_status=lsf_primary_status)

        return _WEBHOOK_TO_TRIGGER.get(current_status)

    def update_poll_after(self):
        if self.latest_status.status in _TERMINAL_STATUSES:
            self.poll_after = None
        else:
            s = object_session(self)
            s.query(Job).filter_by(id=self.id).update({
                'poll_after': self.polling_interval + datetime.datetime.now(),
            })

    def submit(self):
        return lsf.submit(str(self.command), options=self.options,
                          rlimits=self.rlimits)

    @property
    def as_dict(self):
        result = {
            'command': self.command,
            'cwd': self.cwd,
            'status': self.latest_status.status,
            'statusHistory': [h.as_dict for h in self.status_history],
            'webhooks': self.webhooks,
        }

        if self.poll_after:
            result['pollAfter'] = self.poll_after.isoformat()

        self._conditional_add(result, 'options', 'options')
        self._conditional_add(result, 'rlimits', 'rLimits')
        self._conditional_add(result, 'lsf_job_id', 'lsfJobId')

        return result

    def _conditional_add(self, result, prop, name):
        value = getattr(self, prop)
        if value is not None:
            result[name] = value

    def trigger_webhook(self, webhook_name):
        if webhook_name:
            webhook_url = self.webhooks.get(webhook_name)
            if webhook_url:
                celery.current_app.tasks[
'ptero_lsf.implementation.celery_tasks.http_callback.HTTPCallbackTask'
                ].delay(webhook_url, **self.as_dict)


_STATUS_MAP = {
    'DONE': 'SUCCEEDED',
    'EXIT': 'FAILED',
    'PEND': 'SCHEDULED',
    'PSUSP': 'SUSPENDED',
    'RUN': 'RUNNING',
    'SSUSP': 'SUSPENDED',
    'USUSP': 'SUSPENDED',
    'WAIT': 'WAITING',
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
    job_id = Column(Integer, ForeignKey(Job.id), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now(),
                       nullable=False)

    status = Column(Text, index=True, nullable=False)

    lsf_primary_status = Column(Text, index=True)
    lsf_status_set = Column(JSON)

    job = relationship(Job,
                       backref=backref('status_history', order_by=timestamp))

    @property
    def as_dict(self):
        result = {
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
        }

        if self.lsf_primary_status is not None:
            result['lsfPrimaryStatus'] = self.lsf_primary_status

        if self.lsf_status_set is not None:
            result['lsfStatusSet'] = self.lsf_status_set

        return result
