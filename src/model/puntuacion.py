"""Modelo que representa la puntuacion de un usuario"""

# External libraries
from pydantic import BaseModel, Field


class Puntuacion(BaseModel):
    usuario_id: str
    puntuacion: int = Field(..., ge=1, le=5, description="Puntuación entre 1 y 5 estrellas")
