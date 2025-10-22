"""Modelo que representa la puntuacion de un usuario"""

# External libraries
from pydantic import BaseModel, Field


class Puntuacion(BaseModel):
    """Representa la puntuacion que recibe una publicacion"""

    usuario_id: str
    """ID del usuario que puntua"""
    puntuacion: int = Field(
        ..., ge=1, le=5, description="Puntuación entre 1 y 5 estrellas"
    )
    """Puntuacion entre 1 y 5 estrellas"""
