"""Módulo de excepciones personalizadas para UCOfit API."""

from .custom_exceptions import (
    UCOfitException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    EmailError,
    FileError,
    TokenError,
    BusinessLogicError,
)

__all__ = [
    "UCOfitException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "DatabaseError",
    "EmailError",
    "FileError",
    "TokenError",
    "BusinessLogicError",
]
