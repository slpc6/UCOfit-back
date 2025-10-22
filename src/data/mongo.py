"""Conexion con la base de datos de mongo"""

import os

from threading import Lock
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


class MongoDBClientSingleton:
    """Instacia unica para conxion con la base de datos de mongo"""

    _instance = None
    """Instancia unica de la clase"""

    _lock = Lock()
    """Lock para la sincronizacion de la instancia"""

    def __new__(cls):
        """Crea una instancia unica de la clase"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MongoDBClientSingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        """Inicializa la instancia de la clase"""
        if self._initialized:
            return
        load_dotenv()
        mongo_ulr = os.getenv("MONGO_URI")
        self.client = MongoClient(mongo_ulr, server_api=ServerApi("1"))
        try:
            self.client.admin.command("ping")
        except Exception as e:
            print(e)
        self._initialized = True


    def get_collection(self, database: str, collection: str):
        """Obtiene una coleccion de la base de datos

        Args:
            database: Nombre de la base de datos
            collection: Nombre de la coleccion

        Returns:
            Coleccion de la base de datos

        """
        db = self.client[database]
        return db[collection]
