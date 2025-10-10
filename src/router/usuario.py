"""Router para la gestion de usuarios de la aplicacion UCOfit"""

from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

import bcrypt
import jwt

from model.usuario import Usuario, UsuarioActualizar
from util.load_data import get_auth, get_mongo_data, get_secrets

router = APIRouter(prefix="/usuario", tags=["usuario"])
OA2 = get_auth()
DATA = get_mongo_data()
SECRET_KEY, ALGORITHM = get_secrets()


@router.post(path="/registrar")
def registrar(usuario: Usuario) -> JSONResponse:
    """Metodo para crear un usuario nuevo
    
    Args:
    - Usuario: Datos del usuario que se esta registrando
    
    Returns:
    - JSONResponse: Respuesta de la API
    
    """
    try:
        usuario.validarUsuario()
        usuario_dict = usuario.model_dump()

        if DATA.find_one({"email": usuario_dict["email"]}):
            return JSONResponse(
                status_code=400, 
                content={"msg": "Ya existe un usuario con ese correo."})

        usuario_dict["password"] = bcrypt.hashpw(
            usuario_dict["password"].encode('utf-8'), 
            bcrypt.gensalt())

        DATA.insert_one(usuario_dict)
        return JSONResponse(
            status_code=201, 
            content={"msg": "Usuario registrado correctamente"})

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"msg": f"Ocurrio un error inesperado: {e}"})


def datos_usuario(token: str = Depends(OA2)) -> dict:
    """Metodo para des encriptar la informacion del usuario
    
    Args:
    - token: Token de autenticación
    
    Returns:
    - dict: Datos del usuario autenticado
    
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        user = DATA.find_one({"email": payload["email"]}, {"password": 0})
        return user
    except jwt.ExpiredSignatureError as e:
        raise HTTPException(status_code= 401, detail= "Token expirado") from e
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code= 401, detail= "Token inválido") from e


@router.get("/perfil")
def perfil(token: str = Depends(OA2)) -> JSONResponse:
    """Devuelve la información del usuario autenticado
    
    Args:
    - token: Token de autenticación
    
    Returns:
    - JSONResponse: Respuesta de la API
    
    """

    try:
        user = datos_usuario(token)
        if not user:
            return JSONResponse(
                status_code=404,
                content={"data": "Usuario no encontrado"})
    
        user["_id"] = str(user["_id"])
        return JSONResponse(status_code=200, content={"usuario": user})

    except Exception as e:
        return JSONResponse(status_code=500, content={"data": f"Error al obtener la información del usuario: {e}"})


@router.put("/actualizar")
def actualizar(usuario: UsuarioActualizar, token: str = Depends(OA2)) -> JSONResponse:
    """Metodo para actualizar los detalles del usuario
    
    Args:
    - token: Token de autenticación
    - usuario: Nuevos datos para el usuario
    
    Returns:
    - JSONResponse: Respuesta de la API
    """
    try:
        db_usuario = datos_usuario(token)
        if not db_usuario:
            return JSONResponse(status_code=404, content={"msg": "Usuario no encontrado"})
        
        datos_dict = {k: v for k, v in usuario.model_dump().items() if v is not None}
        if "password" in datos_dict:
            datos_dict["password"] = bcrypt.hashpw(
                datos_dict["password"].encode("utf-8"), bcrypt.gensalt())

        DATA.update_one({"email": db_usuario["email"]}, {"$set": datos_dict})
        return JSONResponse(
            content={"msg": "Usuario actualizado correctamente"},
            status_code=200)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"msg": f"Error al actualizar el usuario: {e}"}
        )


@router.delete("/eliminar")
def eliminar(usuario: dict = Depends(OA2)) -> JSONResponse:
    """Elimina un usuario de la base de datos

    :args:
    - usuario: datos del usuario que sera eliminado y que cuenta con los campos prensente en models/usuario.
    - collection: instancia de la base de datos.

    :Returns:
    Un Jsonresponse con un mensaje indicando si se pudo eliminar correctamente el usuario.

    """
    try:
        DATA.delete_one({"email": usuario["email"]})
        return JSONResponse(
            status_code=200, content={"msg": "Usuario eliminado correctamente"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"msg": f"Error al eliminar el usuario: {e}"}
        )
