"""Modulo para manejar las rutas de la aplicacion"""

import os


class Path:
    """Clase para administriar las diferentes rutas del proyecto"""

    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    """Ruta base del proyecto"""

    ROUTERS = os.path.join(ROOT, "router")
    """Ruta a la carpeta de los endpoits de la api"""

    MODELS = os.path.join(ROOT, "model")
    """Ruta a la carpeta de las entidades de dominio"""

    UTIL = os.path.join(ROOT, "util")
    """Ruta a la carpeta de los utilitarios de la aplicacion"""
