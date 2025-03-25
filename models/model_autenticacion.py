"""Modelo para el token de autenticacion"""

# External libraries
from pydantic import BaseModel


class Token(BaseModel):
    """Modelo para el token de autenticacion"""

    access_token: str
    token_type: str
