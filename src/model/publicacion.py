"""Modelo que representa una publicacion"""

from pydantic import BaseModel
from datetime import datetime

from model.comentario import Comentario


class Publicacion(BaseModel):
    """Modelo que representa una publicacion"""

    titulo: str
    """Titulo de la publicacion"""

    descripcion: str
    """Descripcion de la publicacion"""

    descripcion: str
    """Duracion de la publicacion"""

    video: str
    """Video de la publicacion"""

    usuario_id: str
    """ID del usuario que publico la publicacion"""

    puntuacion: int
    """Puntuacion de la publicacion"""

    comentarios: list[Comentario | None]
    """Comentarios de la publicacion"""

    fecha_creacion: datetime
    """Fecha de creacion de la publicacion"""

    fecha_actualizacion: datetime
    """Fecha de actualizacion de la publicacion"""
