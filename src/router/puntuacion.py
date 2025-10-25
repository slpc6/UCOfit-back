"""Router para la gestión de puntuaciones de publicaciones"""

from datetime import datetime
from bson import ObjectId
from fastapi.params import Depends
from fastapi.responses import JSONResponse
from fastapi import APIRouter

from model.puntuacion import Puntuacion
from router.usuario import datos_usuario
from util.load_data import get_mongo_data
from exceptions.custom_exceptions import NotFoundError, BusinessLogicError, DatabaseError


router = APIRouter(prefix="/puntuacion", tags=["puntuacion"])


@router.post("/puntuar/{publicacion_id}")
def puntuar_publicacion(
    publicacion_id: str, puntuacion: Puntuacion, usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Permite puntuar una publicación (1-5 estrellas)

    Args:
    - publicacion_id: ID de la publicación a puntuar
    - puntuacion: Puntuación del usuario (1-5)
    - usuario: datos del usuario autenticado

    Returns:
    - JSONResponse con el estado de la operación
    """
    try:
        collection = get_mongo_data("publicacion")
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            raise NotFoundError("Publicación")

        usuario_id = usuario.get("email", "")
        puntuaciones_existentes = publicacion.get("puntuaciones", [])
        for p in puntuaciones_existentes:
            if p.get("usuario_id") == usuario_id:
                raise BusinessLogicError("Ya has puntuado esta publicación")

        if not 1 <= puntuacion.puntuacion <= 5:
            raise BusinessLogicError("La puntuación debe estar entre 1 y 5")

        nueva_puntuacion = {
            "usuario_id": usuario_id,
            "puntuacion": puntuacion.puntuacion,
            "fecha": datetime.now(),
        }
        collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$push": {"puntuaciones": nueva_puntuacion}},
        )
        puntuaciones_actualizadas = puntuaciones_existentes + [nueva_puntuacion]
        promedio = sum(p["puntuacion"] for p in puntuaciones_actualizadas) / len(
            puntuaciones_actualizadas
        )
        collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$set": {"puntuacion_promedio": round(promedio, 2)}},
        )

        return JSONResponse(status_code=201, content={"msg": "Puntuación registrada correctamente"})

    except Exception as e:
        raise DatabaseError(f"Error al puntuar la publicación: {str(e)}") from e


@router.get("/promedio/{publicacion_id}")
def obtener_promedio_puntuacion(publicacion_id: str) -> JSONResponse:
    """Obtiene el promedio de puntuaciones de una publicación

    Args:
    - publicacion_id: ID de la publicación

    Returns:
    - JSONResponse con el promedio y detalles de puntuaciones
    """
    try:
        collection = get_mongo_data("publicacion")
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            raise NotFoundError("Publicación")

        puntuaciones = publicacion.get("puntuaciones", [])

        if not puntuaciones:
            return JSONResponse(
                status_code=200,
                content={"promedio": 0, "total_puntuaciones": 0, "puntuaciones": []},
            )

        promedio = sum(p["puntuacion"] for p in puntuaciones) / len(puntuaciones)
        puntuaciones_formateadas = []
        for p in puntuaciones:
            p_formateada = p.copy()
            if isinstance(p_formateada.get("fecha"), datetime):
                p_formateada["fecha"] = p_formateada["fecha"].isoformat()
            puntuaciones_formateadas.append(p_formateada)

        return JSONResponse(
            status_code=200,
            content={
                "promedio": round(promedio, 2),
                "total_puntuaciones": len(puntuaciones),
                "puntuaciones": puntuaciones_formateadas,
            },
        )

    except Exception as e:
        raise DatabaseError(f"Error al obtener puntuaciones: {str(e)}") from e
