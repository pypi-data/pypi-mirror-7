from __future__ import absolute_import
import json
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import VARCHAR
from sqlalchemy.dialects import postgresql


class Mapping(TypeDecorator):
    """Platform-independent mapping type.

    When using a PostgreSQL backend the native HSTORE type is used. On
    other databases values are stored as JSON-encoded string.

    Please note that this does not support any of the operators available
    for the `PostgreSQL HSTORE type
    <http://docs.sqlalchemy.org/en/rel_0_9/dialects/postgresql.html#sqlalchemy.dialects.postgresql.HSTORE>`_
    on other dialects.
    """

    impl = postgresql.HSTORE

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return self.impl
        else:
            return dialect.type_descriptor(VARCHAR)

    def process_bind_param(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        else:
            if value is not None:
                value = json.dumps(value)
            return value

    def process_result_value(self, value, dialect):
        if dialect.name == 'postgresql':
            return value
        else:
            if value is not None:
                value = json.loads(value)
            return value
