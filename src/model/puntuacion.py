"""Modelo que representa la puntuacion de un usuario"""

# External libraries
from pydantic import BaseModel


class Puntuacion(BaseModel):
    usuario_id: str
    puntuacion: int
