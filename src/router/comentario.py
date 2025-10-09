"""Router para la gestion de comentarios de las publicaciones"""

# External libraries
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from datetime import datetime

# Local imports
from data.mongo import MongoDBClientSingleton
from router.usuario import datos_usuario

router = APIRouter(prefix="/comentario", tags=["comentario"])


@router.post("/comentar/{publicacion_id}")
def comentar_publicacion(
    publicacion_id: str, comentario: str, usuario: dict = Depends(datos_usuario)
):
    """Añade un comentario a una publicación

    :args:
    - publicacion_id: id de la publicación.
    - comentario: texto del comentario.
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    #collection = get_client(database="UCOfit", collection="publicacion")

    try:
        #publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})

        if not publicacion:
            return JSONResponse(
                content={"msg": "Publicación no encontrada"}, status_code=404
            )

        comentario_data = {
            "usuario_id": usuario["email"],
            "texto": comentario,
            "fecha": str(datetime.now()),
        }
        #publicacion["comentarios"].append(comentario_data)

        #collection.update_one({"_id": ObjectId(publicacion_id)}, {"$set": publicacion})

        return JSONResponse(
            content={"msg": "Comentario añadido con éxito"}, status_code=201
        )
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al añadir comentario: {e}"}, status_code=500
        )


@router.get("/mis_comentarios/")
def obtener_comentarios(usuario: dict = Depends(datos_usuario)):
    """Obtiene todos los comentarios de un usuario

    :args:
        - usuario: datos del usuario autenticado.

    :Returns:
        - Un JSONResponse con los comentarios del usuario.
    """
    collection = get_client(database="UCOfit", collection="publicacion")
    comentarios = collection.find({"comentarios.usuario_id": usuario["email"]})
    return comentarios


@router.put("/editar_comentario/{publicacion_id}/{comentario_id}")
def editar_comentario(
    publicacion_id: str,
    comentario_id: str,
    comentario: str,
    usuario: dict = Depends(datos_usuario),
):
    """Edita un comentario de una publicación

    :args:
        - publicacion_id: id de la publicación.
        - comentario_id: id del comentario.
        - comentario: texto del comentario.
        - usuario: datos del usuario autenticado.

    :Returns:
        - Un JSONResponse con mensaje de éxito o error.
    """
    #collection = get_client(database="UCOfit", collection="publicacion")
    #publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
    if not publicacion:
        return JSONResponse(
            content={"msg": "Publicación no encontrada"}, status_code=404
        )
    #comentario = next(
        (c for c in publicacion["comentarios"] if c["_id"] == ObjectId(comentario_id)),
        None,
    #)
    if not comentario:
        return JSONResponse(
            content={"msg": "Comentario no encontrado"}, status_code=404
        )
    if comentario["usuario_id"] != usuario["email"]:
        return JSONResponse(
            content={"msg": "No tienes permisos para editar este comentario"},
            status_code=403,
        )
    comentario["texto"] = comentario
    #collection.update_one({"_id": ObjectId(publicacion_id)}, {"$set": publicacion})
    return JSONResponse(
        content={"msg": "Comentario editado con éxito"}, status_code=200
    )


@router.delete("/eliminar_comentario/{publicacion_id}/{comentario_id}")
def eliminar_comentario(
    publicacion_id: str, comentario_id: str, usuario: dict = Depends(datos_usuario)
):
    """Elimina un comentario de una publicación

    :args:
        - publicacion_id: id de la publicación.
        - comentario_id: id del comentario.
        - usuario: datos del usuario autenticado.

    :Returns:
        - Un JSONResponse con mensaje de éxito o error.
    """
    #collection = get_client(database="UCOfit", collection="publicacion")
    #publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
    #if not publicacion:
    #    return JSONResponse(
    #        content={"msg": "Publicación no encontrada"}, status_code=404
    #    )
    #comentario = next(
    #    (c for c in publicacion["comentarios"] if c["_id"] == ObjectId(comentario_id)),
    #   None,
    #)
    #if not comentario:
    #    return JSONResponse(
    #        content={"msg": "Comentario no encontrado"}, status_code=404
    #    )
    #collection.update_one({"_id": ObjectId(publicacion_id)}, {"$set": publicacion})
    return JSONResponse(
        content={"msg": "Comentario eliminado con éxito"}, status_code=200
    )
