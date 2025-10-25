"""Módulo para la gestión de autenticación de usuarios."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from model.autenticacion import Token
from util.load_data import get_auth, get_mongo_data, get_secrets
from exceptions.custom_exceptions import (
    AuthenticationError,
    NotFoundError,
    TokenError,
    DatabaseError,
)

router = APIRouter(prefix="/usuario", tags=["usuario"])
OA2 = get_auth()
DATA = get_mongo_data()
SECRET_KEY, ALGORITHM = get_secrets()


@router.post(path="/login")
def login(usuario: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Método para iniciar sesión.

    Args:
        usuario: Datos del usuario que se está iniciando sesión

    Returns:
        Token: Token de acceso JWT

    Raises:
        NotFoundError: Si el usuario no existe
        AuthenticationError: Si la contraseña es incorrecta
        TokenError: Si hay error generando el token
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        db_user = DATA.find_one({"email": str(usuario.username)})

        if not db_user:
            raise NotFoundError("Usuario")

        if not bcrypt.checkpw(str(usuario.password).encode("utf-8"), db_user["password"]):
            raise AuthenticationError("Contraseña incorrecta")

        expire = datetime.now(timezone.utc) + timedelta(hours=2)
        payload = {"sub": str(db_user["_id"]), "email": db_user["email"], "exp": expire}
        token = jwt.encode(payload, SECRET_KEY, ALGORITHM)
        return Token(access_token=token)

    except (NotFoundError, AuthenticationError, TokenError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al iniciar sesión: {str(e)}") from e


@router.post("/logout")
def logout(_: str = Depends(OA2)) -> JSONResponse:
    """Método para cerrar la sesión del usuario.

    Args:
        token: Token de la sesión del usuario

    Returns:
        JSONResponse: Respuesta de la API confirmando el logout

    Raises:
        DatabaseError: Si hay error al procesar el logout
    """
    try:
        return JSONResponse(status_code=200, content={"msg": "Sesión cerrada correctamente"})

    except Exception as e:
        raise DatabaseError(f"Error al cerrar sesión: {str(e)}") from e
