"""Router para la gestion de usuarios de la aplicacion UCOfit"""

# External libraries
from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import JSONResponse

# Internal libraries
from databases.client_mongo import get_client
from models.model_usuario import Usuario
from routers.router_autenticacion import get_current_user

router = APIRouter(prefix='/usuario',
                   tags=['User'])


@router.post(path='/registrar')
def register(usuario: Usuario) -> JSONResponse:
    """Crea un nuevo usuario
    
        :args:
        - usuario: datos del usuario que sera registrado y que cuenta con los campos prensente en models/usuario.
        - collection: instancia de la base de datos.

        :Returns:
        Un Jsonresponse con un mensaje indicando si se pudo registrar correctamente el usuario.
    """
    collection = get_client('UCOfit', 'usuarios')
    if collection.find_one({'email': str(usuario.model_dump()['email'])}):
        return JSONResponse(status_code=400, content={'msg': 'Ya existe un usuario con ese correo'})
    collection.insert_one(usuario.model_dump())
    return JSONResponse(status_code=201, content={'msg': 'Usuario registrado correctamente'})


@router.delete('/delete')
def delete(usuario: dict = Depends(get_current_user)) -> JSONResponse:
    """Elimina un usuario de la base de datos
    
        :args:
        - usuario: datos del usuario que sera eliminado y que cuenta con los campos prensente en models/usuario.
        - collection: instancia de la base de datos.

        :Returns:
        Un Jsonresponse con un mensaje indicando si se pudo eliminar correctamente el usuario.
    """
    collection = get_client('UCOfit', 'usuarios')
    collection.delete_one({'email': usuario['email']})
    return JSONResponse(status_code=200, content={'msg': 'Usuario eliminado correctamente'})
