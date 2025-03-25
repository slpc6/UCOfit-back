"""Este modulo contiene las rutas y funciones para la autenticacion de usuarios en la API"""

# External libraries
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import os

# Internal libraries
from models.model_autenticacion import Token
from databases.client_mongo import get_client


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

router = APIRouter(prefix="", tags=["Autenticacion"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def authenticate_user(email: str, password: str) -> dict:
    """Autentica un usuario en la base de datos

    :args:
    - email: correo del usuario que se desea autenticar.
    - password: contraseña del usuario que se desea autenticar.

    :Returns:
    - Un diccionario con los datos del usuario si este existe en la base de datos, de lo contrario None.

    """
    collection = get_client("UCOfit", "usuarios")
    user = collection.find_one({"email": email})

    if not user:
        return None

    if not password or user["password"] != password:
        return None

    # Eliminar el _id de MongoDB que no es serializable
    if "_id" in user:
        user.pop("_id")

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token de acceso para un usuario

    :args:
    - data: datos del usuario que se desean codificar en el token.
    - expires_delta: tiempo de expiracion del token.

    :Returns:
    - Un token de acceso codificado con los datos del usuario y el tiempo de expiracion.

    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {"exp": expire.timestamp()}
    )  # Usar timestamp en lugar de objeto datetime
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Autentica un usuario en la base de datos y crea un token de acceso

    :args:
    - form_data: datos del formulario que se reciben en la peticion POST.

    :Returns:
    - Un token de acceso si las credenciales son correctas, de lo contrario un mensaje de error.

    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear el token con una expiración explícita
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "rol": user["rol"]},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Obtiene el usuario actual a partir de un token de acceso

    :args:
    - token: token de acceso que se recibe en la peticion.

    :Returns:
    - Un diccionario con los datos del usuario si el token es valido, de lo contrario un mensaje de error.

    """
    collection = get_client("UCOfit", "usuarios")
    credentials_exception = HTTPException(
        status_code=401,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        user = collection.find_one({"email": email})
        if not user:
            raise credentials_exception

        # Eliminamos el _id de MongoDB que no es serializable
        if "_id" in user:
            user.pop("_id")

        return user

    except JWTError:
        raise credentials_exception
