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

        if not 1 <= puntuacion.puntuacion <= 5:
            raise BusinessLogicError("La puntuación debe estar entre 1 y 5")

        # Verificar si el usuario ya puntuó
        ya_puntuado = False
        for i, p in enumerate(puntuaciones_existentes):
            if p.get("usuario_id") == usuario_id:
                # Si ya puntuó, reemplazar su puntuación anterior
                puntuaciones_existentes[i] = {
                    "usuario_id": usuario_id,
                    "puntuacion": puntuacion.puntuacion,
                    "fecha": datetime.now(),
                }
                ya_puntuado = True
                break

        if not ya_puntuado:

            nueva_puntuacion = {
                "usuario_id": usuario_id,
                "puntuacion": puntuacion.puntuacion,
                "fecha": datetime.now(),
            }
            puntuaciones_existentes.append(nueva_puntuacion)

        collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$set": {"puntuaciones": puntuaciones_existentes}},
        )

        promedio = sum(p["puntuacion"] for p in puntuaciones_existentes) / len(
            puntuaciones_existentes
        )
        collection.update_one(
            {"_id": ObjectId(publicacion_id)},
            {"$set": {"puntuacion_promedio": round(promedio, 2)}},
        )

        mensaje = "Puntuación actualizada correctamente" if ya_puntuado else "Puntuación registrada correctamente"

        puntuaciones_formateadas = []
        for p in puntuaciones_existentes:
            p_formateada = p.copy()
            if isinstance(p_formateada.get("fecha"), datetime):
                p_formateada["fecha"] = p_formateada["fecha"].isoformat()
            puntuaciones_formateadas.append(p_formateada)

        return JSONResponse(
            status_code=201,
            content={
                "msg": mensaje,
                "promedio": round(promedio, 2),
                "total_puntuaciones": len(puntuaciones_existentes),
                "puntuaciones": puntuaciones_formateadas
            }
        )

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
