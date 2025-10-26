"""Router para la gestión de retos"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from bson.objectid import ObjectId
from gridfs import GridFS

from model.reto import (
    Reto,
    RetoCrear,
    RetoActualizar,
    RetoResponse,
    RetoConPublicacionRequest,
    RetoConPublicacionResponse,
)
from model.publicacion import Publicacion
from router.usuario import datos_usuario
from util.load_data import get_mongo_data
from util.json_utils import limpiar_datos_para_json
from exceptions.custom_exceptions import (
    DatabaseError,
    BusinessLogicError,
    NotFoundError,
    AuthorizationError,
)


router = APIRouter(prefix="/reto", tags=["reto"])

RETOS_COLLECTION = get_mongo_data("retos")
USUARIOS_COLLECTION = get_mongo_data("usuarios")
PUBLICACIONES_COLLECTION = get_mongo_data("publicaciones")


def check_user_challenge_limit(user_id: str) -> bool:
    """Verifica si el usuario puede crear más retos este mes

    Args:
        user_id: ID del usuario

    Returns:
        bool: True si puede crear más retos
    """
    now = datetime.now()
    first_day_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    retos_este_mes = RETOS_COLLECTION.count_documents(
        {"creador_id": user_id, "_id": {"$gte": ObjectId.from_datetime(first_day_of_month)}}
    )

    return retos_este_mes < 3


@router.post("/crear")
def crear_reto(reto_data: RetoCrear, usuario: dict = Depends(datos_usuario)) -> JSONResponse:
    """Crea un nuevo reto

    Args:
        reto_data: Datos del reto a crear
        usuario: Usuario autenticado

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:
        user_id = str(usuario["_id"])

        if not check_user_challenge_limit(user_id):
            raise BusinessLogicError("Has alcanzado el límite de 3 retos por mes")

        reto = Reto(titulo=reto_data.titulo, descripcion=reto_data.descripcion, creador_id=user_id)
        reto.validar_reto()
        reto_dict = reto.model_dump()
        RETOS_COLLECTION.insert_one(reto_dict)

        return JSONResponse(status_code=201, content={"msg": "Reto creado exitosamente"})

    except ValueError as e:
        raise BusinessLogicError(str(e)) from e
    except Exception as e:
        raise DatabaseError(f"Error al crear el reto: {str(e)}") from e


@router.get("/listar")
def listar_retos(activos: bool = True, limit: int = 20, offset: int = 0) -> JSONResponse:
    """Lista los retos disponibles

    Args:
        activos: Si solo mostrar retos activos
        limit: Límite de resultados
        offset: Desplazamiento

    Returns:
        JSONResponse: Lista de retos
    """
    try:

        filtro = {}
        if activos:
            filtro["fecha_expiracion"] = {"$gt": datetime.now()}

        retos = RETOS_COLLECTION.find(filtro).sort("_id", -1).skip(offset).limit(limit)

        retos_list = []
        for reto in retos:
            reto_dict = RetoResponse.from_reto(reto).model_dump()
            creador_id = reto.get("creador_id", "")
            if creador_id:
                usuario = USUARIOS_COLLECTION.find_one({"_id": ObjectId(creador_id)})
                if usuario and "email" in usuario:
                    reto_dict["creador_id"] = usuario["email"]

            retos_list.append(reto_dict)

        return JSONResponse(
            status_code=200,
            content=limpiar_datos_para_json({"retos": retos_list, "total": len(retos_list)}),
        )

    except Exception as e:
        raise DatabaseError(f"Error al listar los retos: {str(e)}") from e


@router.get("/{reto_id}")
def obtener_reto(reto_id: str) -> JSONResponse:
    """Obtiene un reto específico

    Args:
        reto_id: ID del reto

    Returns:
        JSONResponse: Datos del reto
    """
    try:
        reto = RETOS_COLLECTION.find_one({"_id": ObjectId(reto_id)})

        if not reto:
            raise NotFoundError("Reto")

        reto_response = RetoResponse.from_reto(reto)

        return JSONResponse(
            status_code=200, content=limpiar_datos_para_json({"reto": reto_response.model_dump()})
        )

    except Exception as e:
        raise DatabaseError(f"Error al obtener el reto: {str(e)}") from e


@router.get("/usuario/{usuario_id}")
def obtener_retos_usuario(usuario_id: str, limit: int = 20, offset: int = 0) -> JSONResponse:
    """Obtiene los retos creados por un usuario

    Args:
        usuario_id: ID del usuario
        limit: Límite de resultados
        offset: Desplazamiento

    Returns:
        JSONResponse: Lista de retos del usuario
    """
    try:
        retos = (
            RETOS_COLLECTION.find({"creador_id": usuario_id})
            .sort("_id", -1)
            .skip(offset)
            .limit(limit)
        )

        retos_list = []
        for reto in retos:
            retos_list.append(RetoResponse.from_reto(reto).model_dump())

        return JSONResponse(
            status_code=200,
            content=limpiar_datos_para_json({"retos": retos_list, "total": len(retos_list)}),
        )

    except Exception as e:
        raise DatabaseError(f"Error al obtener los retos del usuario: {str(e)}") from e


@router.put("/{reto_id}")
def actualizar_reto(
    reto_id: str, reto_data: RetoActualizar, usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Actualiza un reto existente

    Args:
        reto_id: ID del reto
        reto_data: Nuevos datos del reto
        usuario: Usuario autenticado

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:
        user_id = str(usuario["_id"])
        reto = RETOS_COLLECTION.find_one({"_id": ObjectId(reto_id)})
        if not reto:
            raise NotFoundError("Reto")

        if reto["creador_id"] != user_id:
            raise AuthorizationError("No tienes permisos para actualizar este reto")

        publicaciones_count = PUBLICACIONES_COLLECTION.count_documents({"reto_id": reto_id})
        if publicaciones_count > 1:
            return JSONResponse(
                status_code=400,
                content={"msg": "No se puede actualizar un reto con más de una publicación"},
            )

        update_data = {}
        if reto_data.titulo is not None:
            update_data["titulo"] = reto_data.titulo
        if reto_data.descripcion is not None:
            update_data["descripcion"] = reto_data.descripcion

        if update_data:
            RETOS_COLLECTION.update_one({"_id": ObjectId(reto_id)}, {"$set": update_data})

        return JSONResponse(status_code=200, content={"msg": "Reto actualizado exitosamente"})

    except Exception as e:
        raise DatabaseError(f"Error al actualizar el reto: {str(e)}") from e


@router.delete("/{reto_id}")
def eliminar_reto(reto_id: str, usuario: dict = Depends(datos_usuario)) -> JSONResponse:
    """Elimina un reto

    Args:
        reto_id: ID del reto
        usuario: Usuario autenticado

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:
        user_id = str(usuario["_id"])

        reto = RETOS_COLLECTION.find_one({"_id": ObjectId(reto_id)})
        if not reto:
            raise NotFoundError("Reto")

        if reto["creador_id"] != user_id:
            raise AuthorizationError("No tienes permisos para actualizar este reto")

        if not Reto(**reto).can_be_deleted():
            raise BusinessLogicError("No se puede eliminar un reto activo con publicaciones")

        PUBLICACIONES_COLLECTION.delete_many({"reto_id": reto_id})

        RETOS_COLLECTION.delete_one({"_id": ObjectId(reto_id)})

        return JSONResponse(status_code=200, content={"msg": "Reto eliminado exitosamente"})

    except Exception as e:
        raise DatabaseError(f"Error al eliminar el reto: {str(e)}") from e


@router.post("/{reto_id}/agregar-publicacion")
def agregar_publicacion_a_reto(
    reto_id: str, publicacion_id: str, _: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Agrega una publicación a un reto

    Args:
        reto_id: ID del reto
        publicacion_id: ID de la publicación
        usuario: Usuario autenticado

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:

        reto = RETOS_COLLECTION.find_one({"_id": ObjectId(reto_id)})
        if not reto:
            raise NotFoundError("Reto")

        if Reto(**reto).is_expired():
            raise BusinessLogicError("El reto ha expirado")

        publicacion = PUBLICACIONES_COLLECTION.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            raise NotFoundError("Publicación")

        PUBLICACIONES_COLLECTION.update_one(
            {"_id": ObjectId(publicacion_id)}, {"$set": {"reto_id": reto_id}}
        )

        return JSONResponse(
            status_code=200, content={"msg": "Publicación agregada al reto exitosamente"}
        )

    except Exception as e:
        raise DatabaseError(f"Error al agregar la publicación al reto: {str(e)}") from e


@router.post("/limpiar-expirados")
def limpiar_retos_expirados() -> JSONResponse:
    """Limpia los retos expirados y sus publicaciones (endpoint administrativo)

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:

        retos_expirados = RETOS_COLLECTION.find({"fecha_expiracion": {"$lt": datetime.now()}})

        publicaciones_eliminadas = 0
        retos_eliminados = 0

        for reto in retos_expirados:
            reto_id = str(reto["_id"])

            result = PUBLICACIONES_COLLECTION.delete_many({"reto_id": reto_id})
            publicaciones_eliminadas += result.deleted_count

            RETOS_COLLECTION.delete_one({"_id": reto["_id"]})
            retos_eliminados += 1

        return JSONResponse(
            status_code=200,
            content=limpiar_datos_para_json(
                {
                    "msg": "Limpieza completada",
                    "retos_eliminados": retos_eliminados,
                    "publicaciones_eliminadas": publicaciones_eliminadas,
                }
            ),
        )

    except Exception as e:
        raise DatabaseError(f"Error al limpiar los retos expirados: {str(e)}") from e


@router.post("/crear-con-publicacion")
def crear_reto_con_publicacion(
    titulo_reto: str = Form(...),
    descripcion_reto: str = Form(...),
    titulo_publicacion: str = Form(...),
    descripcion_publicacion: str = Form(...),
    video: UploadFile = File(...),
    usuario: dict = Depends(datos_usuario),
) -> RetoConPublicacionResponse:
    """Crea un reto junto con su primera publicación.

    Args:
        titulo_reto: Título del reto
        descripcion_reto: Descripción del reto
        titulo_publicacion: Título de la publicación inicial
        descripcion_publicacion: Descripción de la publicación inicial
        video: Video de la publicación inicial
        usuario: Usuario autenticado

    Returns:
        RetoConPublicacionResponse: Respuesta con los IDs creados

    Raises:
        BusinessLogicError: Si el usuario alcanzó el límite de retos
        ValidationError: Si los datos no son válidos
        DatabaseError: Si hay error en la base de datos
    """
    try:
        user_id = str(usuario["_id"])
        if not check_user_challenge_limit(user_id):
            raise BusinessLogicError("Has alcanzado el límite de 3 retos por mes")

        reto = Reto(
            titulo=titulo_reto,
            descripcion=descripcion_reto,
            creador_id=user_id,
            fecha_expiracion=datetime.now() + timedelta(days=30),
        )

        reto.validar_reto()

        reto_dict = reto.model_dump()
        reto_dict["fecha_expiracion"] = reto.fecha_expiracion
        reto_result = RETOS_COLLECTION.insert_one(reto_dict)
        reto_id = str(reto_result.inserted_id)

        collection = get_mongo_data("publicacion")
        db = collection.database
        fs = GridFS(db)
        file_id = fs.put(
            video.file,
            filename=video.filename,
            content_type=video.content_type or "video/mp4",
        )

        publicacion = Publicacion(
            titulo=titulo_publicacion,
            descripcion=descripcion_publicacion,
            video=str(file_id),
            usuario_id=usuario["email"],
            reto_id=reto_id,
            puntuaciones=[],
            puntuacion_promedio=0,
        )

        publicacion_result = collection.insert_one(publicacion.model_dump())
        publicacion_id = str(publicacion_result.inserted_id)

        return RetoConPublicacionResponse(
            msg="Reto y publicación inicial creados exitosamente",
            reto_id=reto_id,
            publicacion_id=publicacion_id,
            video_id=str(file_id),
        )

    except ValueError as e:
        raise BusinessLogicError(str(e)) from e
    except Exception as e:
        raise DatabaseError(f"Error al crear el reto con publicación: {str(e)}") from e
