"""Modelo que representa los datos del usuario"""

import re

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Usuario(BaseModel):
    """Modelo que representa los datos del usuario"""

    nombre: str
    """Nombre del usuario"""

    apellido: str
    """Apellido del usuario"""

    email: EmailStr
    """Correo electrónico del usuario"""

    password: str
    """Contraseña del usuario"""

    descripcion: str
    """Descripción del usuario"""

    foto_perfil: str = None
    """Foto de perfil del usuario en base64"""

    ciudad: str = None
    """Ciudad del usuario"""

    telefono: str = None
    """Teléfono del usuario"""

    def validar_usuario(self) -> None:
        """Valida todas las reglas de negocio del modelo Usuario.

        Lanza ValueError con el detalle de errores si existe alguna violación.

        Raises:
            ValueError: Si existe alguna violación de las reglas de negocio.

        """
        errores: list[str] = []
        pattern = re.compile(r"^[a-z]+\.[a-z]+\d{4}@uco\.net\.co$")

        if not isinstance(self.nombre.strip(), str) or not 1 <= len(self.nombre) <= 50:
            errores.append("El nombre debe tener entre 1 y 50 caracteres.")

        if not isinstance(self.apellido.strip(), str) or not 1 <= len(self.apellido) <= 50:
            errores.append("El apellido debe tener entre 1 y 50 caracteres.")

        if not isinstance(self.email, str) or not re.match(pattern, self.email):
            errores.append("El correo electrónico no tiene un formato válido.")

        if not isinstance(self.password, str) or not 8 <= len(self.password) <= 128:
            errores.append("La contraseña debe tener entre 8 y 128 caracteres.")

        if not isinstance(self.descripcion.strip(), str) or len(self.descripcion) > 500:
            errores.append("La descripción no puede superar los 500 caracteres.")

        if self.foto_perfil is not None:
            try:

                if not self.foto_perfil.startswith("data:image/jpeg;base64,"):
                    errores.append("La foto de perfil debe ser una imagen JPG válida.")
            except (ValueError, TypeError):
                errores.append(
                    "La foto de perfil debe ser una imagen JPG válida en formato base64."
                )

        if self.ciudad is not None:
            if not isinstance(self.ciudad.strip(), str) or not 3 <= len(self.ciudad.strip()) <= 15:
                errores.append("La ciudad debe tener entre 3 y 15 caracteres.")

        if self.telefono is not None:
            if not isinstance(self.telefono, str) or not re.match(r"^\d{7,10}$", self.telefono):
                errores.append(
                    "El teléfono debe contener entre 7 y 10 dígitos numéricos únicamente."
                )

        if errores:
            raise ValueError("; ".join(errores))


class UsuarioActualizar(BaseModel):
    """Clase que representa los datos que serán actualizados para un usuario existente."""

    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    """Nombre del usuario (opcional)"""

    apellido: Optional[str] = Field(None, min_length=2, max_length=50)
    """Apellido del usuario (opcional)"""

    email: Optional[EmailStr] = None
    """Correo electrónico del usuario (opcional)"""

    password: Optional[str] = Field(None, min_length=6)
    """Contraseña del usuario (opcional)"""

    descripcion: Optional[str] = Field(None, max_length=255)
    """Descripción del usuario (opcional)"""

    foto_perfil: Optional[str] = None
    """Foto de perfil del usuario en base64 (opcional)"""

    ciudad: Optional[str] = Field(None, min_length=3, max_length=15)
    """Ciudad del usuario (opcional)"""

    telefono: Optional[str] = Field(None, pattern=r"^\d{7,10}$")
    """Teléfono del usuario (opcional)"""
