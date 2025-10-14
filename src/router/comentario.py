"""Punto de gestion de los endpoints que involucran manejo de comentarios"""

from bson import ObjectId
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter

from model.comentario import Comentario
from router.usuario import datos_usuario
from util.load_data import get_mongo_data

router = APIRouter(prefix="/comentario", tags=["comentario"])


@router.post("/comentar")
def crear_comentario(
    publicacion_id: str,
    comentario: Comentario,
    usuario: dict = Depends(datos_usuario)) -> JSONResponse:
    """Permite agregar un comentario a una publocacion
    Arg:
    - publicacion_id: Identificador unico de la publicacion a comentar.
    - comentario: Comentario que se agregara a la publicacion.
    - usuario: datos de sesion del usuario que comenta.

    Returns:
    - Jsonresponse con el estado de la solicitud de creacion del comentario.
    """
    try:
        collection = get_mongo_data("publicacion")
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        publicacion["comentario"].append(comentario)
        collection.update_one(publicacion["_id"], publicacion)

        return JSONResponse(status_code=201, content= {"msg": "Comentario Enviado."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"msg": f"Error al enviar el comentario: {e}"})
