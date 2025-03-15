from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from models.model_publicacion import Publicacion
from routers.router_autenticacion import get_current_user
from databases.client_mongo import get_client

router = APIRouter(prefix='/publicacion',
                        tags=['Publicacion'])


@router.post('/crear-publicacion')
def crear_publicacion(publicacion: Publicacion, usuario: dict = Depends(get_current_user)) -> JSONResponse:
    collection = get_client(database='UCOfit', collection='publicacion')
    
    try:
        usuario_id = str(usuario['_id'])
        publicacion.usuario_id = usuario_id
        publicacion = collection.insert_one(publicacion.model_dump())
    except Exception as e:
        return JSONResponse(content={'msg': f'Error al crear la publicacion {e}'}, status_code=500)
    return JSONResponse(content={'msg': 'Publicacion creada con exito'}, status_code=201)


@router.get('/listar-publicacion')
def eliminar_publicacion(usuario: dict = Depends(get_current_user)):
    print(usuario)
    return {'msg': 'eliminar_publicacion'}


@router.put('/editar-publicacion')
def editar_publicacion():
    return {'msg': 'editar_publicacion'}


@router.delete('/eliminar-publicacion')
def eliminar_publicacion():
    return {'msg': 'eliminar_publicacion'}
