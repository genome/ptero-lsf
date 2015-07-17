from sqlalchemy import Integer
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.dialects.postgresql import JSON as psqlJSON
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.functions import GenericFunction
import json
import os


__all__ = ['JSON', 'get_data_element']


# This class (JSONEncodedDict) is taken from
# http://docs.sqlalchemy.org/en/rel_0_9/core/types.html#marshal-json-strings
class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


def get_data_element_brute_force(task, indexes):
    d = task.data
    for i in indexes:
        d = d[i]
    return d


def get_data_element_postgres_extensions(task, indexes):
    if indexes:
        q = task.__class__.data[indexes]
    else:
        q = task.__class__.data

    s = object_session(task)
    tup = s.query(q).filter_by(id=task.id).one()
    return tup[0]


def get_data_size_brute_force(task, indexes):
    d = task.data
    for i in indexes:
        d = d[i]

    if not isinstance(d, list):
        raise RuntimeError('DataError: Data is not a list')
    else:
        return len(d)


class json_array_length(GenericFunction):
    type = Integer


def get_data_size_postgres_extensions(task, indexes):
    if indexes:
        q = task.__class__.data[indexes]
    else:
        q = task.__class__.data

    s = object_session(task)
    tup = s.query(json_array_length(q)).filter_by(id=task.id).one()
    return tup[0]


if os.environ.get('PTERO_WORKFLOW_DB_STRING', 'sqlite://'
        ).startswith('postgres'):

    MutableJSONDict = MutableDict.as_mutable(psqlJSON)
    JSON = psqlJSON
    get_data_element = get_data_element_postgres_extensions
    get_data_size = get_data_size_postgres_extensions

else:
    MutableJSONDict = MutableDict.as_mutable(JSONEncodedDict(1000))
    JSON = JSONEncodedDict(1000)
    get_data_element = get_data_element_brute_force
    get_data_size = get_data_size_brute_force
