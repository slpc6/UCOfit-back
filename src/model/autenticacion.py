"""Modelo para el token de autenticacion"""

from pydantic import BaseModel


class Token(BaseModel):
    """Modelo para el token de autenticacion"""

    access_token: str
    """Token de acceso"""

    token_type: str = "Bearer"
    """Tipo de token"""
