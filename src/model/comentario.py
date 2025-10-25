"""Modelo que representa las características que tiene un comentario."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Comentario(BaseModel):
    """Clase que representa un comentario."""

    comentario_id: str
    """Identificador único del comentario"""

    usuario_id: str
    """Usuario que comenta la publicación"""

    comentario: str
    """Mensaje ingresado por el usuario"""

    fecha: datetime
    """Fecha y hora del comentario"""


class ComentarioCrearRequest(BaseModel):
    """Modelo para crear un nuevo comentario."""

    comentario: str = Field(..., min_length=1, max_length=500)
    """Mensaje del comentario"""

    publicacion_id: str
    """ID de la publicación a comentar"""


class ComentarioResponse(BaseModel):
    """Modelo de respuesta para comentarios."""

    comentario_id: str
    """ID del comentario"""

    usuario_id: str
    """ID del usuario que comentó"""

    comentario: str
    """Mensaje del comentario"""

    fecha: str
    """Fecha del comentario en formato ISO"""

    nombre_usuario: Optional[str] = None
    """Nombre del usuario que comentó"""
