"""Script que permite obtener variables globales."""

import os

from fastapi.security import OAuth2PasswordBearer
from data.mongo import MongoDBClientSingleton


def get_auth() -> OAuth2PasswordBearer:
    """Retorna la variable para la protección de rutas que requieren usuarios logueados.

    Returns:
        OAuth2PasswordBearer: Variable con el token de sesión del usuario
    """
    oa2 = OAuth2PasswordBearer(tokenUrl="/usuario/login")
    return oa2


def get_mongo_data(coleccion: str = "usuarios"):
    """Retorna la conexión con la base de datos de MongoDB.

    Args:
        coleccion: Nombre de la colección que se busca en la BD

    Returns:
        Collection: Conexión con la base de datos buscada
    """
    data = MongoDBClientSingleton().get_collection("UCOfit", coleccion)
    return data


def get_secrets() -> tuple[str, str]:
    """Retorna las claves de encriptación de datos.

    Returns:
        Tupla con los valores cargados de las variables de encriptación
    """
    key = os.getenv("SECRET_KEY")
    alg = os.getenv("ALGORITHM")

    if not key or not alg:
        raise ValueError("SECRET_KEY o ALGORITHM no están configurados")

    return key, alg
