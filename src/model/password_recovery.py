"""Modelo para la recuperación de contraseña"""

from pydantic import BaseModel, EmailStr


class PasswordRecoveryRequest(BaseModel):
    """Modelo para solicitar recuperación de contraseña"""

    email: EmailStr
    """Correo electrónico del usuario"""


class PasswordResetRequest(BaseModel):
    """Modelo para resetear la contraseña"""

    token: str
    """Token de recuperación"""

    new_password: str
    """Nueva contraseña"""


class TokenValidationResponse(BaseModel):
    """Modelo para respuesta de validación de token"""

    valid: bool
    """Indica si el token es válido"""

    msg: str
    """Mensaje de respuesta"""
