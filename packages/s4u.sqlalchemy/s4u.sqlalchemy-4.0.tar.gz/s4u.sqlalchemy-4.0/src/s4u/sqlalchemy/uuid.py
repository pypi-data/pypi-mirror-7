from __future__ import absolute_import
import uuid
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import CHAR
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses CHAR(36), storing as
    stringified hex values.

    This implementation is based on the SQLAlchemy 
    `backend-agnostic GUID Type
    <http://www.sqlalchemy.org/docs/core/types.html#backend-agnostic-guid-type>`_
    example.
    """
    impl = CHAR

    python_type = type('')

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return self.python_type(value)
        else:
            if not isinstance(value, uuid.UUID):
                return self.python_type(uuid.UUID(value))
            else:
                # hexstring
                return self.python_type(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return self.python_type(value)
