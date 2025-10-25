"""Punto de gestion de los endpoints que involucran manejo de comentarios"""

from datetime import datetime
from bson import ObjectId
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter

from model.comentario import Comentario
from router.usuario import datos_usuario
from util.load_data import get_mongo_data
from exceptions.custom_exceptions import DatabaseError, NotFoundError


router = APIRouter(prefix="/comentario", tags=["comentario"])


@router.post("/comentar/{publicacion_id}")
def crear_comentario(
    publicacion_id: str, comentario: Comentario, usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Permite agregar un comentario a una publocacion
    Arg:
    - publicacion_id: Identificador unico de la publicacion a comentar.
    - comentario: Comentario que se agregara a la publicacion.
    - usuario: datos de sesion del usuario que comenta.

    Returns:
    - Jsonresponse con el estado de la solicitud de creacion del comentario.

    Raises:
    - NotFoundError: Si la publicacion no existe.
    - DatabaseError: Si hay error en la base de datos.
    """
    try:
        collection = get_mongo_data("publicacion")

        nuevo_comentario = comentario.model_dump()
        nuevo_comentario["usuario_id"] = usuario.get("email", "")
        nuevo_comentario["comentario_id"] = str(ObjectId())
        nuevo_comentario["fecha"] = datetime.now()

        result = collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$push": {"comentarios": nuevo_comentario}},
        )

        if result.matched_count == 0:
            raise NotFoundError("Publicación")

        return JSONResponse(status_code=201, content={"msg": "Comentario enviado."})

    except Exception as e:
        raise DatabaseError(f"Error al enviar el comentario: {str(e)}") from e
