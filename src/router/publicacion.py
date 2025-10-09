from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from typing import Optional

from model.publicacion import Publicacion
from router.usuario import datos_usuario

router = APIRouter(prefix="/publicacion", tags=["Publicacion"])


@router.post("/crear")
def crear_publicacion(
    publicacion: Publicacion, usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Crea una nueva publicación en la base de datos

    :args:
    - publicacion: datos de la publicación a crear.
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    #collection = get_client(database="UCOfit", collection="publicacion")

    try:
        publicacion_dict = publicacion.model_dump()
        publicacion_dict["usuario_id"] = usuario["email"]
        publicacion_dict["comentarios"] = []
        publicacion_dict["puntuacion"] = 0

    #    collection.insert_one(publicacion_dict)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al crear la publicación: {e}"}, status_code=500
        )

    return JSONResponse(
        content={"msg": "Publicación creada con éxito"}, status_code=201
    )


@router.get("/general")
def listar_publicaciones(usuario: dict = Depends(datos_usuario)):
    """Lista todas las publicaciones disponibles

    :args:
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con la lista de publicaciones.
    """
    #collection = get_client(database="UCOfit", collection="publicacion")
"""
    try:
    #    publicaciones = list(collection.find())
    
        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])
    
        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al listar publicaciones: {e}"}, status_code=500
        )"""


@router.get("/usuario")
def listar_publicaciones_usuario(usuario: dict = Depends(datos_usuario)):
    """Lista todas las publicaciones de un usuario específico

    :args:
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con la lista de publicaciones del usuario.
    """
    """collection = get_client(database="UCOfit", collection="publicacion")

    try:
        publicaciones = list(collection.find({"usuario_id": usuario["email"]}))

        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])

        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al listar publicaciones del usuario: {e}"},
            status_code=500,
        )
"""

@router.put("/editar")
def editar_publicacion(
    publicacion_id: str,
    titulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    video: Optional[str] = None,
    usuario: dict = Depends(datos_usuario),
):
    """Actualiza una publicación existente

    :args:
    - publicacion_id: id de la publicación a editar.
    - titulo: nuevo título (opcional).
    - descripcion: nueva descripción (opcional).
    - video: nuevo enlace al video (opcional).
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    """
    collection = get_client(database="UCOfit", collection="publicacion")

    try:
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})

        if not publicacion:
            return JSONResponse(
                content={"msg": "Publicación no encontrada"}, status_code=404
            )

        if publicacion.get("usuario_id") != usuario["email"]:
            return JSONResponse(
                content={"msg": "No tienes permiso para editar esta publicación"},
                status_code=403,
            )

        update_data = {}
        if titulo:
            update_data["titulo"] = titulo
        if descripcion:
            update_data["descripcion"] = descripcion
        if video:
            update_data["video"] = video

        if not update_data:
            return JSONResponse(
                content={"msg": "No se proporcionaron datos para actualizar"},
                status_code=400,
            )

        collection.update_one({"_id": ObjectId(publicacion_id)}, {"$set": update_data})

        return JSONResponse(
            content={"msg": "Publicación actualizada con éxito"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al editar la publicación: {e}"}, status_code=500
        )"""


@router.delete("/eliminar/{publicacion_id}")
def eliminar_publicacion(
    publicacion_id: str, usuario: dict = Depends(datos_usuario)
):
    """Elimina una publicación existente

    :args:
    - publicacion_id: id de la publicación a eliminar.
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    """collection = get_client(database="UCOfit", collection="publicacion")

    try:
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})

        if not publicacion:
            return JSONResponse(
                content={"msg": "Publicación no encontrada"}, status_code=404
            )

        if (
            publicacion.get("usuario_id") != usuario["email"]
            and usuario.get("rol") != "administrador"
        ):
            return JSONResponse(
                content={"msg": "No tienes permiso para eliminar esta publicación"},
                status_code=403,
            )

        collection.delete_one({"_id": ObjectId(publicacion_id)})

        return JSONResponse(
            content={"msg": "Publicación eliminada con éxito"}, status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al eliminar la publicación: {e}"}, status_code=500
        )"""
