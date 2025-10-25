"""Punto de gestión de los endpoints que involucran manejo de comentarios."""

from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from model.comentario import ComentarioCrearRequest
from router.usuario import datos_usuario
from util.load_data import get_mongo_data
from exceptions.custom_exceptions import DatabaseError, NotFoundError


router = APIRouter(prefix="/comentario", tags=["comentario"])


@router.post("/comentar/{publicacion_id}")
def crear_comentario(
    publicacion_id: str, datos: ComentarioCrearRequest, usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Permite agregar un comentario a una publicación.

    Args:
        publicacion_id: Identificador único de la publicación a comentar
        datos: Datos del comentario a crear
        usuario: Datos de sesión del usuario que comenta

    Returns:
        JSONResponse: Estado de la solicitud de creación del comentario

    Raises:
        NotFoundError: Si la publicación no existe
        DatabaseError: Si hay error en la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")

        nuevo_comentario = {
            "comentario_id": str(ObjectId()),
            "usuario_id": usuario.get("email", ""),
            "comentario": datos.comentario,
            "fecha": datetime.now(),
        }

        result = collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$push": {"comentarios": nuevo_comentario}},
        )

        if result.matched_count == 0:
            raise NotFoundError("Publicación")

        return JSONResponse(status_code=201, content={"msg": "Comentario enviado."})

    except Exception as e:
        raise DatabaseError(f"Error al enviar el comentario: {str(e)}") from e
