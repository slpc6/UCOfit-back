"""Excepciones personalizadas para UCOfit API."""

from typing import Optional, Dict, Any


class UCOfitException(Exception):
    """Excepción base para todas las excepciones de UCOfit.

    Attributes:
        message: Mensaje descriptivo del error
        status_code: Código de estado HTTP asociado
        details: Detalles adicionales del error
    """

    def __init__(
        self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None
    ):
        """Inicializa la excepción.

        Args:
            message: Mensaje descriptivo del error
            status_code: Código de estado HTTP (default: 500)
            details: Detalles adicionales del error
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(UCOfitException):
    """Excepción para errores de validación de datos.

    Se lanza cuando los datos proporcionados no cumplen con las reglas de validación.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Inicializa la excepción de validación.

        Args:
            message: Mensaje descriptivo del error de validación
            details: Detalles específicos de los errores de validación
        """
        super().__init__(message, 400, details)


class AuthenticationError(UCOfitException):
    """Excepción para errores de autenticación.

    Se lanza cuando las credenciales son inválidas o el usuario no está autenticado.
    """

    def __init__(self, message: str = "Credenciales inválidas"):
        """Inicializa la excepción de autenticación.

        Args:
            message: Mensaje descriptivo del error de autenticación
        """
        super().__init__(message, 401)


class AuthorizationError(UCOfitException):
    """Excepción para errores de autorización.

    Se lanza cuando el usuario no tiene permisos para realizar una acción.
    """

    def __init__(self, message: str = "No tienes permisos para realizar esta acción"):
        """Inicializa la excepción de autorización.

        Args:
            message: Mensaje descriptivo del error de autorización
        """
        super().__init__(message, 403)


class NotFoundError(UCOfitException):
    """Excepción para recursos no encontrados.

    Se lanza cuando un recurso solicitado no existe en la base de datos.
    """

    def __init__(self, resource: str = "Recurso"):
        """Inicializa la excepción de recurso no encontrado.

        Args:
            resource: Nombre del recurso que no se encontró
        """
        message = f"{resource} no encontrado"
        super().__init__(message, 404)


class DatabaseError(UCOfitException):
    """Excepción para errores de base de datos.

    Se lanza cuando ocurre un error al interactuar con la base de datos.
    """

    def __init__(self, message: str = "Error en la base de datos"):
        """Inicializa la excepción de base de datos.

        Args:
            message: Mensaje descriptivo del error de base de datos
        """
        super().__init__(message, 500)


class EmailError(UCOfitException):
    """Excepción para errores relacionados con el envío de emails.

    Se lanza cuando ocurre un error al enviar emails.
    """

    def __init__(self, message: str = "Error al enviar el email"):
        """Inicializa la excepción de email.

        Args:
            message: Mensaje descriptivo del error de email
        """
        super().__init__(message, 500)


class FileError(UCOfitException):
    """Excepción para errores relacionados con archivos.

    Se lanza cuando ocurre un error al procesar archivos.
    """

    def __init__(self, message: str = "Error al procesar el archivo"):
        """Inicializa la excepción de archivo.

        Args:
            message: Mensaje descriptivo del error de archivo
        """
        super().__init__(message, 400)


class TokenError(UCOfitException):
    """Excepción para errores relacionados con tokens JWT.

    Se lanza cuando hay problemas con la generación, validación o decodificación de tokens.
    """

    def __init__(self, message: str = "Error con el token"):
        """Inicializa la excepción de token.

        Args:
            message: Mensaje descriptivo del error de token
        """
        super().__init__(message, 401)


class BusinessLogicError(UCOfitException):
    """Excepción para errores de lógica de negocio.

    Se lanza cuando se violan reglas de negocio específicas de la aplicación.
    """

    def __init__(self, message: str, status_code: int = 400):
        """Inicializa la excepción de lógica de negocio.

        Args:
            message: Mensaje descriptivo del error de lógica de negocio
            status_code: Código de estado HTTP (default: 400)
        """
        super().__init__(message, status_code)
