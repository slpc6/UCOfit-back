
from fastapi.security import OAuth2PasswordBearer

import os


from data.mongo import MongoDBClientSingleton


def get_auth():
    OA2 = OAuth2PasswordBearer(tokenUrl="/usuario/login")
    return OA2

def get_mongo_data():
    DATA = MongoDBClientSingleton().get_collection("UCOfit", "usuarios")
    return DATA

def get_secrets():
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    return SECRET_KEY, ALGORITHM
