from fastapi import APIRouter


router = APIRouter(prefix='/publicacion',
                        tags=['Publicacion'])


@router.post('/crear-publicacion')
def crear_publicacion():
    return {'msg': 'crear_publicacion'}