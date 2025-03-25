"""Router para la gestion de comentarios de las publicaciones"""

#External libraries
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from datetime import datetime

#Local imports
from routers.router_autenticacion import get_current_user
from databases.client_mongo import get_client
from models.model_comentario import Comentario


router = APIRouter(prefix='/comentario', tags=['comentario'])


@router.post('/comentar/{publicacion_id}')
def comentar_publicacion(
    publicacion_id: str, 
    comentario: str,
    usuario: dict = Depends(get_current_user)
):
    """Añade un comentario a una publicación
    
        :args:
        - publicacion_id: id de la publicación.
        - comentario: texto del comentario.
        - usuario: datos del usuario autenticado.
        
        :Returns:
        - Un JSONResponse con mensaje de éxito o error.
    """
    collection = get_client(database='UCOfit', collection='publicacion')
    
    try:
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})

        if not publicacion:
            return JSONResponse(content={'msg': 'Publicación no encontrada'}, status_code=404)
        
        comentario_data = { 
            "usuario_id": usuario["email"],
            "texto": comentario,
            "fecha": str(datetime.now())
        }
        publicacion["comentarios"].append(comentario_data)
        
        collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$set": publicacion}  
        )
        
        return JSONResponse(content={'msg': 'Comentario añadido con éxito'}, status_code=201)
    except Exception as e:
        return JSONResponse(content={'msg': f'Error al añadir comentario: {e}'}, status_code=500)
