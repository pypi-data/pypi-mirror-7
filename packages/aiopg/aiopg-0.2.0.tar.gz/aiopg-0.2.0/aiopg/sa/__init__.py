"""Optional support for sqlalchemy.sql dynamic query generation."""

from .engine import create_engine, dialect, Engine
from .connection import SAConnection
from .exc import (Error, ArgumentError, InvalidRequestError,
                  NoSuchColumnError, ResourceClosedError)


__all__ = ('dialect', 'create_engine', 'SAConnection', 'Error',
           'ArgumentError', 'InvalidRequestError', 'NoSuchColumnError',
           'ResourceClosedError', 'Engine')


(SAConnection, Error, ArgumentError, InvalidRequestError,
 NoSuchColumnError, ResourceClosedError, create_engine, dialect, Engine)
