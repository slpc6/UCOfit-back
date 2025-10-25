"""Middleware para manejo centralizado de excepciones."""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .custom_exceptions import UCOfitException


async def ucofit_exception_handler(request: Request, exc: UCOfitException) -> JSONResponse:
    """Manejador para excepciones personalizadas de UCOfit.

    Args:
        request: Request de FastAPI
        exc: Excepción personalizada de UCOfit

    Returns:
        JSONResponse: Respuesta JSON con el error
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "request": request.url,
            "error": exc.message,
            "details": exc.details,
            "status_code": exc.status_code,
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Manejador para excepciones HTTP estándar.

    Args:
        request: Request de FastAPI
        exc: Excepción HTTP

    Returns:
        JSONResponse: Respuesta JSON con el error
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"request": request.url, "error": exc.detail, "status_code": exc.status_code},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Manejador para errores de validación de Pydantic.

    Args:
        request: Request de FastAPI
        exc: Excepción de validación

    Returns:
        JSONResponse: Respuesta JSON con los errores de validación
    """
    return JSONResponse(
        status_code=422,
        content={
            "request": request.url,
            "error": "Error de validación",
            "details": exc.errors(),
            "status_code": 422,
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Manejador para excepciones generales no capturadas.

    Args:
        request: Request de FastAPI
        exc: Excepción general

    Returns:
        JSONResponse: Respuesta JSON con error genérico
    """
    return JSONResponse(
        status_code=500,
        content={
            "request": request.url,
            "error": "Error interno del servidor",
            "details": str(exc),
            "status_code": 500,
        },
    )
