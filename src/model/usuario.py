"""Modelo que representa los datos del usuario"""

# External libraries
import re
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Usuario(BaseModel):
    """Modelo que representa los datos del usuario"""

    nombre: str
    """Nombre del usuario"""

    apellido: str
    """Apellido del usuario"""

    email: str
    """Correo electrónico del usuario"""

    password: str
    """Contraseña del usuario"""

    descripcion: str
    """Descripción del usuario"""


    def validarUsuario(self) -> None:
        """Valida todas las reglas de negocio del modelo Usuario.

        Lanza ValueError con el detalle de errores si existe alguna violación.

        Raises:
            ValueError: Si existe alguna violación de las reglas de negocio.
        
        """
        errores: list[str] = []

        if not isinstance(self.nombre, str) or not (1 <= len(self.nombre) <= 50):
            errores.append("El nombre debe tener entre 1 y 50 caracteres.")

        if not isinstance(self.apellido, str) or not (1 <= len(self.apellido) <= 50):
            errores.append("El apellido debe tener entre 1 y 50 caracteres.")

        # Validación de email simple
        if not isinstance(self.email, str) or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", self.email):
            errores.append("El correo electrónico no tiene un formato válido.")

        if not isinstance(self.password, str) or not (8 <= len(self.password) <= 128):
            errores.append("La contraseña debe tener entre 8 y 128 caracteres.")

        if not isinstance(self.descripcion, str) or len(self.descripcion) > 500:
            errores.append("La descripción no puede superar los 500 caracteres.")

        if errores:
            raise ValueError("; ".join(errores))


class UsuarioActualizar(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    apellido: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    descripcion: Optional[str] = Field(None, max_length=255)
