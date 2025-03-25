# Clase que gestiona las rutas dentro del proyecto

# External libraries
import os


class path:
    root = os.path.dirname(os.path.abspath(__file__))
    """Ruta raiz del proyecto."""

    routers = os.path.join(root, "routers")
    """Ruta con los diferentes routers para los modulos de la aplicacion."""
