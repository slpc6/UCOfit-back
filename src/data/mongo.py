"""Conexion con la base de datos de mongo"""

import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.read_preferences import Primary
from pymongo.server_api import ServerApi
from threading import Lock


class MongoDBClientSingleton:
    _instance = None
    _lock = Lock()


    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MongoDBClientSingleton, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance


    def __init__(self):
        if self._initialized:
            return
        load_dotenv()
        MONGO_URI = os.getenv("MONGO_URI")
        self.client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
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
