"""Modelo que representa las caracteristicas que tiene un comentario"""

from datetime import datetime
from pydantic import BaseModel


class Comentario(BaseModel):
    """Clase que representa un comentario"""

    comentario_id: str
    """Identificador unico del comentario"""

    usuario_id: str
    """Usuario que comenta la publicacion"""

    comentario: str
    """Mensaje ingresado por el usuario"""

    fecha: datetime
    """Fecha y hora del comentario"""
