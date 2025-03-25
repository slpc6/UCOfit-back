"""Modelo que representa una publicacion"""

# External libraries
from pydantic import BaseModel

# Internal imports
from models.model_comentario import Comentario


class Publicacion(BaseModel):
    titulo: str
    descripcion: str
    video: str
    usuario_id: str
    comentarios: list[Comentario | None]
    puntuacion: int
