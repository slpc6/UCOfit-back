"""Router para la gestión de usuarios de la aplicación UCOfit."""

import bcrypt
import jwt

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from model.usuario import Usuario, UsuarioActualizar
from util.load_data import get_auth, get_mongo_data, get_secrets
from exceptions.custom_exceptions import ValidationError, NotFoundError, DatabaseError, TokenError

router = APIRouter(prefix="/usuario", tags=["usuario"])
OA2 = get_auth()
DATA = get_mongo_data()
SECRET_KEY, ALGORITHM = get_secrets()


@router.post(path="/registrar")
def registrar(usuario: Usuario) -> JSONResponse:
    """Método para crear un usuario nuevo.

    Args:
        usuario: Datos del usuario que se está registrando

    Returns:
        JSONResponse: Respuesta de la API

    Raises:
        ValidationError: Si los datos del usuario no son válidos
        DatabaseError: Si hay error en la base de datos
    """
    try:
        usuario.validar_usuario()
        usuario_dict = usuario.model_dump()

        if DATA.find_one({"email": usuario_dict["email"]}):
            raise ValidationError("Ya existe un usuario con ese correo.")

        usuario_dict["password"] = bcrypt.hashpw(
            usuario_dict["password"].encode("utf-8"), bcrypt.gensalt()
        )

        DATA.insert_one(usuario_dict)
        return JSONResponse(status_code=201, content={"msg": "Usuario registrado correctamente"})

    except ValidationError:
        raise
    except Exception as e:
        raise DatabaseError(f"Error al registrar usuario: {str(e)}") from e


def datos_usuario(token: str = Depends(OA2)) -> dict:
    """Método para desencriptar la información del usuario.

    Args:
        token: Token de autenticación

    Returns:
        dict: Datos del usuario autenticado

    Raises:
        TokenError: Si el token es inválido o expirado
        NotFoundError: Si el usuario no existe
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user = DATA.find_one({"email": payload["email"]}, {"password": 0})

        if not user:
            raise NotFoundError("Usuario")

        return user

    except jwt.ExpiredSignatureError as e:
        raise TokenError("Token expirado") from e
    except jwt.InvalidTokenError as e:
        raise TokenError("Token inválido") from e
    except Exception as e:
        raise DatabaseError(f"Error al obtener datos del usuario: {str(e)}") from e


@router.get("/perfil")
def perfil(token: str = Depends(OA2)) -> JSONResponse:
    """Devuelve la información del usuario autenticado.

    Args:
        token: Token de autenticación

    Returns:
        JSONResponse: Respuesta de la API con los datos del usuario

    Raises:
        NotFoundError: Si el usuario no existe
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        user = datos_usuario(token)
        user["_id"] = str(user["_id"])
        return JSONResponse(status_code=200, content={"usuario": user})

    except (NotFoundError, TokenError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al obtener perfil: {str(e)}") from e


@router.put("/actualizar")
def actualizar(usuario: UsuarioActualizar, token: str = Depends(OA2)) -> JSONResponse:
    """Método para actualizar los detalles del usuario.

    Args:
        usuario: Nuevos datos para el usuario
        token: Token de autenticación

    Returns:
        JSONResponse: Respuesta de la API

    Raises:
        NotFoundError: Si el usuario no existe
        DatabaseError: Si hay error actualizando el usuario
    """
    try:
        db_usuario = datos_usuario(token)

        datos_dict = {k: v for k, v in usuario.model_dump().items() if v is not None}

        if "password" in datos_dict:
            datos_dict["password"] = bcrypt.hashpw(
                datos_dict["password"].encode("utf-8"), bcrypt.gensalt()
            )

        DATA.update_one({"email": db_usuario["email"]}, {"$set": datos_dict})
        return JSONResponse(content={"msg": "Usuario actualizado correctamente"}, status_code=200)

    except (NotFoundError, TokenError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al actualizar usuario: {str(e)}") from e


@router.delete("/eliminar")
def eliminar(token: str = Depends(OA2)) -> JSONResponse:
    """Elimina un usuario de la base de datos.

    Args:
        token: Token de autenticación

    Returns:
        JSONResponse: Respuesta de la API confirmando la eliminación

    Raises:
        NotFoundError: Si el usuario no existe
        DatabaseError: Si hay error eliminando el usuario
    """
    try:
        usuario = datos_usuario(token)
        DATA.delete_one({"email": usuario["email"]})
        return JSONResponse(status_code=200, content={"msg": "Usuario eliminado correctamente"})

    except (NotFoundError, TokenError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al eliminar usuario: {str(e)}") from e
