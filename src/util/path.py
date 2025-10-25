"""Módulo para manejar las rutas de la aplicación."""

import os


class Path:
    """Clase para administrar las diferentes rutas del proyecto."""

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    """Ruta base del proyecto."""

    ROUTERS = os.path.join(ROOT, "router")
    """Ruta a la carpeta de los endpoints de la API."""

    MODELS = os.path.join(ROOT, "model")
    """Ruta a la carpeta de las entidades de dominio."""

    UTIL = os.path.join(ROOT, "util")
    """Ruta a la carpeta de los utilitarios de la aplicación."""

    VIDEO = "https://ucofit-back.onrender.com/publicacion/video"
    """Ruta donde se buscarán los videos para mostrar al usuario."""
