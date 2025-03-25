"""Modelo que representa los datos del usuario"""

# External libraries
from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class Usuario(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Nombre del usuario (2-50 caracteres)",
    )
    apellido: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Apellido del usuario (2-50 caracteres)",
    )
    email: EmailStr = Field(..., description="Correo electrónico válido")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña (mínimo 8 caracteres)",
    )
    descripcion: str = Field(
        "", max_length=500, description="Descripción opcional (máximo 500 caracteres)"
    )
    rol: Literal["administrador", "usuario"] = Field(
        ..., description="Rol del usuario (administrador, usuario)"
    )
    puntuacion: int = Field(
        ..., description="Puntuación del usuario"
    )
