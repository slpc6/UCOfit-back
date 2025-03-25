"""Router para la gestion de puntuaciones de las publicaciones"""

# External imports
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

# Local imports
from routers.router_autenticacion import get_current_user
from databases.client_mongo import get_client


router = APIRouter(prefix="/puntuacion", tags=["puntuacion"])


@router.post("/puntuar/{publicacion_id}")
def puntuar_publicacion(
    publicacion_id: str, puntuacion: int, usuario: dict = Depends(get_current_user)
):
    """Añade o actualiza la puntuación de una publicación

    :args:
    - publicacion_id: id de la publicación.
    - puntuacion: valor de la puntuación (1-5).
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    collection = get_client(database="UCOfit", collection="publicacion")

    if puntuacion < 1 or puntuacion > 5:
        return JSONResponse(
            content={"msg": "La puntuación debe estar entre 1 y 5"}, status_code=400
        )

    try:
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})

        if not publicacion:
            return JSONResponse(
                content={"msg": "Publicación no encontrada"}, status_code=404
            )

        publicacion["puntuacion"] = (publicacion["puntuacion"] + puntuacion) / 2
        collection.update_one({"_id": ObjectId(publicacion_id)}, {"$set": publicacion})

        usuario["puntuacion"] = (usuario["puntuacion"] + puntuacion)
        collection.update_one({"_id": ObjectId(usuario["email"])}, {"$set": usuario})

        return JSONResponse(
            content={"msg": "Puntuación actualizada con éxito"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al puntuar publicación: {e}"}, status_code=500
        )


@router.get('/ranking_usuarios')
def obtener_ranking_usuarios(usuario: dict = Depends(get_current_user)):
    """Obtiene el ranking de usuarios por puntuación
    
    :Returns:
    - Un JSONResponse con el ranking de usuarios.
    """
    collection = get_client(database='UCOfit', collection='usuarios')
    usuarios = collection.find().sort('puntuacion', -1)
    usuarios_list = []
    for usuario in usuarios:
        usuario["_id"] = str(usuario["_id"])
        usuarios_list.append(usuario)
        
    return JSONResponse(content={"usuarios": usuarios_list}, status_code=200)
