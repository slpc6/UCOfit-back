"""Modelo que representa una publicación."""

from pydantic import BaseModel
from model.puntuacion import Puntuacion


class Publicacion(BaseModel):
    """Modelo que representa una publicación."""

    titulo: str
    """Título de la publicación"""

    descripcion: str
    """Descripción de la publicación"""

    video: str
    """ID del video de la publicación en GridFS"""

    usuario_id: str
    """ID del usuario que publicó la publicación"""

    reto_id: str
    """ID del reto al que pertenece la publicación"""

    puntuaciones: list[Puntuacion]
    """Lista de puntuaciones de la publicación"""

    puntuacion_promedio: float
    """Puntuación promedio de la publicación"""

    def validar_publicacion(self) -> None:
        """Valida las reglas de negocio para una publicación.

        Raises:
            ValueError: Si existe alguna violación de las reglas de negocio.
        """
        errores: list[str] = []

        if not isinstance(self.titulo, str) or not 5 <= len(self.titulo) <= 30:
            errores.append("El título debe tener entre 5 y 30 caracteres.")

        if not isinstance(self.descripcion, str) or not 10 <= len(self.descripcion) <= 100:
            errores.append("La descripción debe tener entre 10 y 100 caracteres.")

        if not self.reto_id:
            errores.append("La publicación debe pertenecer a un reto.")

        if errores:
            raise ValueError("; ".join(errores))
