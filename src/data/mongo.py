"""Conexión con la base de datos de MongoDB."""

import os
from threading import Lock

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoDBClientSingleton:
    """Instancia única para conexión con la base de datos de MongoDB."""

    _instance = None
    """Instancia única de la clase."""

    _lock = Lock()
    """Lock para la sincronización de la instancia."""

    _initialized = False
    """Flag para verificar si la instancia está inicializada."""

    def __new__(cls):
        """Crea una instancia única de la clase."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MongoDBClientSingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa la instancia de la clase."""
        if self._initialized:
            return

        load_dotenv()
        mongo_url = os.getenv("MONGO_URI")

        if not mongo_url:
            raise ValueError("MONGO_URI no está configurada en las variables de entorno")

        self.client = MongoClient(mongo_url, server_api=ServerApi("1"))

        try:
            self.client.admin.command("ping")
        except Exception as e:
            raise ConnectionError(f"Error conectando a MongoDB: {e}") from e

        self._initialized = True

    def get_collection(self, database: str, collection: str):
        """Obtiene una colección de la base de datos.

        Args:
            database: Nombre de la base de datos
            collection: Nombre de la colección

        Returns:
            Colección de la base de datos
        """
        db = self.client[database]
        return db[collection]
