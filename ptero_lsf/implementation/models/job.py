from .base import Base
from json_type import JSON
from sqlalchemy import Column, func
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import backref, relationship


__all__ = ['Job']


class Job(Base):
    __tablename__ = 'job'

    id = Column(Integer, primary_key=True)

    command = Column(Text, nullable=False)
    options = Column(JSON)
    rlimits = Column(JSON)

    created_at = Column(DateTime(timezone=True), default=func.now(),
                        nullable=False)
    status = Column(Text, index=True, nullable=False)

    lsf_job_id = Column(Integer, index=True)

    lsf_primary_status = Column(Text, index=True)
    lsf_status_set = Column(JSON)

    def update_status(self, lsf_status_set):
        current_status = _extract_status(lsf_status_set)
        lsf_primary_status = _extract_primary_status(lsf_status_set)
        lsf_sorted_statuses = sorted(lsf_status_set)

        self.status = current_status
        self.lsf_primary_status = lsf_primary_status
        self.lsf_status_set = lsf_sorted_statuses

        JobStatusHistory(job=self, status=current_status,
                         lsf_status_set=lsf_sorted_statuses,
                         lsf_primary_status=lsf_primary_status)

    @property
    def as_dict(self):
        result = {
            'command': self.command,
            'status': self.status,
            'statusHistory': [h.as_dict for h in self.status_history],
        }

        self._conditional_add(result, 'options', 'options')
        self._conditional_add(result, 'rlimits', 'rLimits')
        self._conditional_add(result, 'lsf_job_id', 'lsfJobId')
        self._conditional_add(result, 'lsf_primary_status', 'lsfPrimaryStatus')
        self._conditional_add(result, 'lsf_status_set', 'lsfStatusSet')

        return result

    def _conditional_add(self, result, prop, name):
        value = getattr(self, prop)
        if value is not None:
            result[name] = value


def _extract_status(lsf_status_set):
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
