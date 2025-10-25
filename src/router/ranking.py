"""Router para el sistema de puntuación y ranking"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId

from router.usuario import datos_usuario
from util.load_data import get_mongo_data
from util.json_utils import limpiar_datos_para_json
from exceptions.custom_exceptions import DatabaseError


router = APIRouter(prefix="/ranking", tags=["ranking"])


USUARIOS_COLLECTION = get_mongo_data("usuarios")
PUBLICACIONES_COLLECTION = get_mongo_data("publicacion")
PUNTUACIONES_COLLECTION = get_mongo_data("puntuacion")


def calcular_puntuacion_usuario(usuario_id: str) -> dict:
    """Calcula la puntuación total de un usuario

    Args:
        usuario_id: ID del usuario

    Returns:
        dict: Datos de puntuación del usuario
    """
    try:
        usuario = USUARIOS_COLLECTION.find_one({"_id": ObjectId(usuario_id)})
        if not usuario:

            return {
                "puntuacion_total": 0.0,
                "total_publicaciones": 0,
                "promedio_puntuacion": 0.0,
                "publicaciones_con_puntuacion": 0,
            }

        publicaciones = PUBLICACIONES_COLLECTION.find({"usuario_id": usuario["email"]})
        publicaciones_list = list(publicaciones)

        puntuacion_total = 0.0
        publicaciones_con_puntuacion = 0
        promedio_puntuacion = 0.0
        total_publicaciones = 0

        for publicacion in publicaciones_list:
            total_publicaciones += 1
            puntuacion_total += publicacion.get("puntuacion_promedio", 0)
            for _ in publicacion.get("puntuaciones"):
                publicaciones_con_puntuacion += 1
        if publicaciones_con_puntuacion > 0:
            promedio_puntuacion = puntuacion_total / publicaciones_con_puntuacion
        resultado = {
            "puntuacion_total": round(puntuacion_total, 2),
            "total_publicaciones": total_publicaciones,
            "promedio_puntuacion": round(promedio_puntuacion, 2),
            "publicaciones_con_puntuacion": publicaciones_con_puntuacion,
        }
        return resultado

    except Exception as e:
        raise DatabaseError(f"Error calculando puntuación para {usuario_id}: {str(e)}") from e


@router.get("/general")
def obtener_ranking_general(limit: int = 50, offset: int = 0) -> JSONResponse:
    """Obtiene el ranking general de usuarios

    Args:
        limit: Límite de resultados
        offset: Desplazamiento

    Returns:
        JSONResponse: Ranking de usuarios
    """
    try:

        usuarios = USUARIOS_COLLECTION.find({}, {"password": 0})
        usuarios_list = list(usuarios)
        ranking_data = []

        for usuario in usuarios_list:
            usuario_id = str(usuario["_id"])
            puntuacion_data = calcular_puntuacion_usuario(usuario_id)

            ranking_data.append(
                {
                    "usuario_id": usuario_id,
                    "nombre": usuario["nombre"],
                    "apellido": usuario["apellido"],
                    "email": usuario["email"],
                    "foto_perfil": usuario.get("foto_perfil"),
                    "ciudad": usuario.get("ciudad"),
                    **puntuacion_data,
                }
            )

        ranking_data.sort(key=lambda x: x["puntuacion_total"], reverse=True)

        for i, usuario in enumerate(ranking_data):
            usuario["posicion"] = i + 1

        ranking_paginado = ranking_data[offset : offset + limit]

        return JSONResponse(
            status_code=200,
            content=limpiar_datos_para_json(
                {
                    "ranking": ranking_paginado,
                    "total": len(ranking_data),
                    "pagina_actual": (offset // limit) + 1,
                    "total_paginas": (len(ranking_data) + limit - 1) // limit,
                }
            ),
        )
    except Exception as e:
        raise DatabaseError(f"Error al obtener el ranking general: {str(e)}") from e


@router.get("/mi-puntuacion")
def obtener_mi_puntuacion(usuario: dict = Depends(datos_usuario)) -> JSONResponse:
    """Obtiene la puntuación del usuario autenticado

    Args:
        usuario: Usuario autenticado

    Returns:
        JSONResponse: Puntuación del usuario
    """
    try:
        usuario_id = str(usuario["_id"])
        puntuacion_data = calcular_puntuacion_usuario(usuario_id)

        usuarios = USUARIOS_COLLECTION.find({}, {"password": 0})
        ranking_data = []

        for user in usuarios:
            user_id = str(user["_id"])
            user_puntuacion = calcular_puntuacion_usuario(user_id)

            ranking_data.append({"usuario_id": user_id, **user_puntuacion})

        ranking_data.sort(key=lambda x: x["puntuacion_total"], reverse=True)

        posicion = 0
        for i, user in enumerate(ranking_data):
            if user["usuario_id"] == usuario_id:
                posicion = i + 1
                break

        return JSONResponse(
            status_code=200,
            content=limpiar_datos_para_json(
                {
                    "usuario": {
                        "usuario_id": usuario_id,
                        "nombre": usuario["nombre"],
                        "apellido": usuario["apellido"],
                        "email": usuario["email"],
                        "foto_perfil": usuario.get("foto_perfil"),
                        "ciudad": usuario.get("ciudad"),
                        **puntuacion_data,
                        "posicion": posicion,
                    }
                }
            ),
        )

    except Exception as e:
        raise DatabaseError(f"Error al obtener la puntuación del usuario: {str(e)}") from e
