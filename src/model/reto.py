"""Modelo que representa un reto"""

from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field


class Reto(BaseModel):
    """Modelo que representa un reto"""

    titulo: str = Field(..., min_length=5, max_length=50)
    """Título del reto"""

    descripcion: str = Field(..., min_length=10, max_length=200)
    """Descripción del reto"""

    creador_id: str
    """ID del usuario que creó el reto"""

    fecha_expiracion: datetime
    """Fecha de expiración del reto (1 mes después de la creación)"""

    def __init__(self, **data):
        super().__init__(**data)

        if not hasattr(self, 'fecha_expiracion') or not self.fecha_expiracion:
            self.fecha_expiracion = datetime.now() + timedelta(days=30)

    def validar_reto(self) -> None:
        """Valida las reglas de negocio del reto

        Raises:
            ValueError: Si existe alguna violación de las reglas de negocio.
        """
        errores: list[str] = []

        if not isinstance(self.titulo, str) or not 5 <= len(self.titulo) <= 50:
            errores.append("El título debe tener entre 5 y 50 caracteres.")

        if not isinstance(self.descripcion, str) or not 10 <= len(self.descripcion) <= 200:
            errores.append("La descripción debe tener entre 10 y 200 caracteres.")

        if self.fecha_expiracion <= datetime.now():
            errores.append("La fecha de expiración debe ser posterior a la fecha actual.")

        if errores:
            raise ValueError("; ".join(errores))

    def is_expired(self) -> bool:
        """Verifica si el reto ha expirado
        
        Returns:
            bool: True si el reto ha expirado
        """
        return datetime.now() > self.fecha_expiracion

    def can_be_deleted(self) -> bool:
        """Verifica si el reto puede ser eliminado
        
        Returns:
            bool: True si el reto puede ser eliminado
        """
        return self.is_expired()


class RetoCrear(BaseModel):
    """Modelo para crear un nuevo reto"""
    titulo: str = Field(..., min_length=5, max_length=50)
    descripcion: str = Field(..., min_length=10, max_length=200)


class RetoActualizar(BaseModel):
    """Modelo para actualizar un reto existente"""
    titulo: Optional[str] = Field(None, min_length=5, max_length=50)
    descripcion: Optional[str] = Field(None, min_length=10, max_length=200)


class RetoResponse(BaseModel):
    """Modelo de respuesta para retos"""
    id: str
    titulo: str
    descripcion: str
    creador_id: str
    fecha_expiracion: datetime
    dias_restantes: int
    is_expired: bool

    @classmethod
    def from_reto(cls, reto_dict: dict) -> "RetoResponse":
        """Crea una respuesta desde un diccionario de reto
        
        Args:
            reto_dict: Diccionario con los datos del reto
            
        Returns:
            RetoResponse: Respuesta formateada
        """
        dias_restantes = 0
        is_expired = False
        
        if reto_dict.get('fecha_expiracion'):
            fecha_exp = reto_dict['fecha_expiracion']
            if isinstance(fecha_exp, str):
                fecha_exp = datetime.fromisoformat(fecha_exp)
            dias_restantes = max(0, (fecha_exp - datetime.now()).days)
            is_expired = dias_restantes == 0

        fecha_expiracion = reto_dict['fecha_expiracion']
        if isinstance(fecha_expiracion, datetime):
            fecha_expiracion = fecha_expiracion.isoformat()

        return cls(
            id=str(reto_dict['_id']),
            titulo=reto_dict['titulo'],
            descripcion=reto_dict['descripcion'],
            creador_id=reto_dict['creador_id'],
            fecha_expiracion=fecha_expiracion,
            dias_restantes=dias_restantes,
            is_expired=is_expired
        )
