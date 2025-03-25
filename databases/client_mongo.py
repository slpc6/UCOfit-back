"""Conexion con la base de datos de mongo"""

# External libraries
import os

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def get_client(database: str, collection: str) -> MongoClient:
    """Establece una conexcion con una base de datos mongo
    :args:
    - database: Nombre de la base de datos
    - collection: Nombre de la coleccion
    :returns:
    - Una instancia con la conexcion a la coleccion espeficica de la base de datos

    """
    load_dotenv()
    CLIENT_MONGO = os.getenv("CLIENT_MONGO")
    client = MongoClient(CLIENT_MONGO, server_api=ServerApi("1"))
    try:
        client.admin.command("ping")
    except Exception as e:
        print(e)

    db = client[database]
    collection = db[collection]

    return collection
