"""Modelo que representa una publicacion"""

from typing import List, Optional
from fastapi import UploadFile
from pydantic import BaseModel


from model.comentario import Comentario


class Publicacion(BaseModel):
    """Modelo que representa una publicacion"""

    titulo: str
    """Titulo de la publicacion"""

    descripcion: str
    """Descripcion de la publicacion"""

    video: UploadFile
    """Video de la publicacion"""

    usuario_id: str
    """ID del usuario que publico la publicacion"""

    comentarios: List[Optional[Comentario]] = []
    """Comentarios de la publicacion"""



    def validar_publicacion(self):
        """Valida las reglas de negocio para una publicacion

        Raises:
            ValueError: Si existe alguna violación de las reglas de negocio.
        """
        errores: list[str] = []

        if not isinstance(self.titulo, str) or not 5 <= len(self.titulo) <= 30:
            errores.append("El titulo debe tener entre 5 y 30 caracteres.")

        if not isinstance(self.descripcion, str) or not 10<= len(self.descripcion) <= 100:
            errores.append("La descripcion debe tener entre 10 y 100 caracteres.")


        if errores:
            raise ValueError("; ".join(errores))
