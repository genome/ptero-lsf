from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.dialects.postgresql import JSON as psqlJSON
import json
import os


__all__ = ['JSON']


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


if os.environ.get('PTERO_LSF_DB_STRING', 'sqlite://').startswith('postgres'):
    JSON = psqlJSON
else:
    JSON = JSONEncodedDict(1000)
