"""Modelo que representa la puntuación de un usuario."""

from pydantic import BaseModel, Field


class Puntuacion(BaseModel):
    """Representa la puntuación que recibe una publicación."""

    usuario_id: str
    """ID del usuario que puntúa"""

    puntuacion: int = Field(..., ge=1, le=5, description="Puntuación entre 1 y 5 estrellas")
    """Puntuación entre 1 y 5 estrellas"""
