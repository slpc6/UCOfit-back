"""Modelo para el token de autenticación."""

from pydantic import BaseModel


class Token(BaseModel):
    """Modelo para el token de autenticación."""

    access_token: str
    """Token de acceso JWT"""

    token_type: str = "Bearer"
    """Tipo de token (siempre Bearer para JWT)"""
