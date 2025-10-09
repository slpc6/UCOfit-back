"""Modulo para la gestion de usuarios"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import os


from model.autenticacion import Token
from util.load_data import get_auth, get_mongo_data, get_secrets

router = APIRouter(prefix="/usuario", 
                   tags=["usuario"])
OA2 = get_auth()
DATA = get_mongo_data()
SECRET_KEY, ALGORITHM = get_secrets()


@router.post(path='/login')
def login(usuario: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Metodo para iniciar sesion
    :args:
    - UsuarioLogin: Datos del usuario que se esta iniciando sesion
    
    :returns:
    - JSONResponse: Respuesta de la API
    
    """
    try:

        db_user = DATA.find_one({"email": str(usuario.username)})

        if not db_user:
            return JSONResponse(status_code=404, content={"msg": "Usuario no encontrado"})
        if not bcrypt.checkpw(str(usuario.password).encode('utf-8'), db_user["password"]):
            return JSONResponse(status_code=400, content={"msg": "Contraseña incorrecta"})
        
        SECRET_KEY = os.getenv("SECRET_KEY")
        ALGORITHM = os.getenv("ALGORITHM")
        expire = datetime.now(timezone.utc) + timedelta(hours=2)
        payload = {
            "sub": str(db_user["_id"]),
            "email": db_user["email"],
            "exp": expire
        }
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        return Token(access_token=token)

    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": f"Error al iniciar sesion: {e}"})


@router.post('/logout')
def loguot(token: str = Depends(OA2)) -> Token:
    try:
        token = ''
        return Token(access_token=token)
    
    except Exception as e:
        JSONResponse(status_code=500, content={"msg": f"Error al obtener usuarios conectados: {e}"})
