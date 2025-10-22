"""Script que permite Obtener variables globales."""

import os
from fastapi.security import OAuth2PasswordBearer


from data.mongo import MongoDBClientSingleton


def get_auth():
    """Retorna la variable para la proteccion de routes que
    requieren usuarios logeados

    :Returns:
    - OAuth2PasswordBearer: Tipo de variable con el token de sesion
    del usuario

    """
    oa2 = OAuth2PasswordBearer(tokenUrl="/usuario/login")
    return oa2


def get_mongo_data(coleccion: str = "usuarios"):
    """Retorna la conexcion con la base de datos de mongo.

    :Ars:
    - coleccion: nombre de la coleccion que se busca en la bd.

    :Returns:
    - Collection: Conexion con la base de datos buscada.

    """
    data = MongoDBClientSingleton().get_collection("UCOfit", coleccion)
    return data


def get_secrets():
    """Retorna las claves de encriptacion de datos
    :Returns:
    - Tupla con los valores cargados de las variables de
    encriptacion.

    """
    key = os.getenv("SECRET_KEY")
    alg = os.getenv("ALGORITHM")
    return key, alg
