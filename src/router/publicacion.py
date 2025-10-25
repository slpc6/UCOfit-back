"""Módulo para la gestión de los endpoints relacionados con publicaciones."""

from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from gridfs import GridFS
from bson.objectid import ObjectId

from router.usuario import datos_usuario
from util.load_data import get_mongo_data
from util.path import Path
from util.json_utils import convertir_fechas_a_string
from model.publicacion import (
    PublicacionCrearRequest,
    PublicacionCrearResponse,
    PublicacionEditarRequest,
)
from exceptions.custom_exceptions import (
    NotFoundError,
    AuthorizationError,
    FileError,
    DatabaseError,
    BusinessLogicError,
    ValidationError,
)

router = APIRouter(prefix="/publicacion", tags=["Publicacion"])


@router.post("/crear")
def crear_publicacion(
    datos: PublicacionCrearRequest,
    video: UploadFile = File(...),
    usuario: dict = Depends(datos_usuario),
) -> PublicacionCrearResponse:
    """Crea una nueva publicación en la base de datos.

    Args:
        datos: Datos de la publicación a crear
        video: Archivo de video enviado como multipart/form-data
        usuario: Datos del usuario autenticado

    Returns:
        PublicacionCrearResponse: Respuesta con el ID de la publicación creada

    Raises:
        NotFoundError: Si el reto no existe
        BusinessLogicError: Si el reto ha expirado
        FileError: Si hay error procesando el archivo
        DatabaseError: Si hay error en la base de datos
    """
    try:
        retos_collection = get_mongo_data("retos")
        reto = retos_collection.find_one({"_id": ObjectId(datos.reto_id)})

        if not reto:
            raise NotFoundError("Reto")

        if datetime.now() > reto["fecha_expiracion"]:
            raise BusinessLogicError("El reto ha expirado")

        collection = get_mongo_data("publicacion")
        db = collection.database
        fs = GridFS(db)

        file_id = fs.put(
            video.file,
            filename=video.filename,
            content_type=video.content_type or "video/mp4",
        )

        publicacion_doc = {
            "titulo": datos.titulo,
            "descripcion": datos.descripcion,
            "video": str(file_id),
            "usuario_id": usuario["email"],
            "reto_id": datos.reto_id,
        }

        result = collection.insert_one(publicacion_doc)
        publicacion_id = str(result.inserted_id)

        return PublicacionCrearResponse(
            msg="Publicación creada con éxito",
            publicacion_id=publicacion_id,
            video_id=str(file_id),
            reto_id=datos.reto_id,
        )

    except (NotFoundError, BusinessLogicError, FileError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al crear la publicación: {str(e)}") from e


@router.get("/general")
def listar_publicaciones(_: dict = Depends(datos_usuario)) -> JSONResponse:
    """Lista todas las publicaciones disponibles con URLs de video integradas.

    Args:
        usuario: Datos del usuario autenticado

    Returns:
        JSONResponse: Lista de publicaciones con URLs de video

    Raises:
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")
        publicaciones = list(collection.find())

        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])
            if "video" in pub and isinstance(pub["video"], str):
                video_id = str(pub["video"])
                pub["video_url"] = f"{Path.VIDEO}/{video_id}"
                pub["video"] = video_id

            convertir_fechas_a_string(pub)

        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)

    except Exception as e:
        raise DatabaseError(f"Error al listar publicaciones: {str(e)}") from e


@router.get("/reto/{reto_id}")
def listar_publicaciones_reto(reto_id: str, _: dict = Depends(datos_usuario)) -> JSONResponse:
    """Lista todas las publicaciones de un reto específico.

    Args:
        reto_id: ID del reto
        usuario: Datos del usuario autenticado

    Returns:
        JSONResponse: Lista de publicaciones del reto

    Raises:
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")
        publicaciones = list(collection.find({"reto_id": reto_id}))

        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])
            if "video" in pub and isinstance(pub["video"], str):
                video_id = str(pub["video"])
                pub["video_url"] = f"{Path.VIDEO}/{video_id}"
                pub["video"] = video_id

            convertir_fechas_a_string(pub)

        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)

    except Exception as e:
        raise DatabaseError(f"Error al listar publicaciones del reto: {str(e)}") from e


@router.get("/video/{video_id}")
def obtener_video_endpoint(video_id: str) -> StreamingResponse:
    """Devuelve el stream del video almacenado en GridFS por su ID.

    Args:
        video_id: ID del video en GridFS

    Returns:
        StreamingResponse: Stream del video

    Raises:
        NotFoundError: Si el video no existe
        FileError: Si hay error accediendo al archivo
    """
    try:
        collection = get_mongo_data("publicacion")
        db = collection.database
        fs = GridFS(db)

        try:
            grid_out = fs.get(ObjectId(video_id))
        except Exception as e:
            raise NotFoundError("Video") from e

        def iterfile():
            chunk = grid_out.read(1024 * 1024)
            while chunk:
                yield chunk
                chunk = grid_out.read(1024 * 1024)

        media_type = (
            getattr(grid_out, "content_type", "application/octet-stream")
            or "application/octet-stream"
        )
        return StreamingResponse(iterfile(), media_type=media_type)

    except NotFoundError:
        raise
    except Exception as e:
        raise FileError(f"Error al obtener el video: {str(e)}") from e


@router.get("/usuario")
def listar_publicaciones_usuario(usuario: dict = Depends(datos_usuario)) -> JSONResponse:
    """Lista todas las publicaciones de un usuario específico con URLs de video integradas.

    Args:
        usuario: Datos del usuario autenticado

    Returns:
        JSONResponse: Lista de publicaciones del usuario con URLs de video

    Raises:
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")
        publicaciones = list(collection.find({"usuario_id": usuario["email"]}))

        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])
            if "video" in pub and isinstance(pub["video"], str):
                video_id = str(pub["video"])
                pub["video_url"] = f"{Path.VIDEO}/{video_id}"
                pub["video"] = video_id

            convertir_fechas_a_string(pub)

        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)

    except Exception as e:
        raise DatabaseError(f"Error al listar publicaciones del usuario: {str(e)}") from e


@router.get("/{publicacion_id}")
def obtener_publicacion(publicacion_id: str) -> JSONResponse:
    """Devuelve una publicación filtrada por ID.

    Args:
        publicacion_id: ID de la publicación a buscar

    Returns:
        JSONResponse: Datos de la publicación encontrada

    Raises:
        NotFoundError: Si la publicación no existe
        DatabaseError: Si hay error accediendo a la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})

        if not publicacion:
            raise NotFoundError("Publicación")

        publicacion["_id"] = str(publicacion["_id"])
        convertir_fechas_a_string(publicacion)

        return JSONResponse(content=publicacion, status_code=200)

    except NotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Error al obtener la publicación: {str(e)}") from e


@router.put("/editar/{publicacion_id}")
def editar_publicacion(
    publicacion_id: str,
    datos: PublicacionEditarRequest,
    usuario: dict = Depends(datos_usuario),
) -> JSONResponse:
    """Actualiza una publicación existente.

    Args:
        publicacion_id: ID de la publicación a editar
        datos: Datos a actualizar en la publicación
        usuario: Datos del usuario autenticado

    Returns:
        JSONResponse: Respuesta de la API confirmando la actualización

    Raises:
        NotFoundError: Si la publicación no existe
        AuthorizationError: Si el usuario no tiene permisos
        ValidationError: Si no se proporcionan datos para actualizar
        DatabaseError: Si hay error en la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")

        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            raise NotFoundError("Publicación")

        if publicacion.get("usuario_id") != usuario["email"]:
            raise AuthorizationError("No tienes permiso para editar esta publicación")

        update_data = {}
        if datos.titulo is not None:
            update_data["titulo"] = datos.titulo
        if datos.descripcion is not None:
            update_data["descripcion"] = datos.descripcion

        if not update_data:
            raise ValidationError("No se proporcionaron datos para actualizar")

        result = collection.update_one({"_id": ObjectId(publicacion_id)}, {"$set": update_data})

        if result.modified_count == 0:
            return JSONResponse(
                content={"msg": "No se realizaron cambios en la publicación"},
                status_code=200,
            )

        return JSONResponse(content={"msg": "Publicación actualizada con éxito"}, status_code=200)

    except (NotFoundError, AuthorizationError, ValidationError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al editar la publicación: {str(e)}") from e


@router.delete("/eliminar/{publicacion_id}")
def eliminar_publicacion(
    publicacion_id: str, usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Elimina una publicación existente.

    Args:
        publicacion_id: ID de la publicación a eliminar
        usuario: Datos del usuario autenticado

    Returns:
        JSONResponse: Respuesta de la API confirmando la eliminación

    Raises:
        NotFoundError: Si la publicación no existe
        AuthorizationError: Si el usuario no tiene permisos
        DatabaseError: Si hay error en la base de datos
    """
    try:
        collection = get_mongo_data("publicacion")

        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            raise NotFoundError("Publicación")

        if publicacion.get("usuario_id") != usuario["email"]:
            raise AuthorizationError("No tienes permiso para eliminar esta publicación")

        if "video" in publicacion and publicacion["video"]:
            try:
                db = collection.database
                fs = GridFS(db)
                fs.delete(ObjectId(publicacion["video"]))
            except Exception as e:
                raise FileError(f"Error al eliminar video de GridFS: {str(e)}") from e

        result = collection.delete_one({"_id": ObjectId(publicacion_id)})

        if result.deleted_count == 0:
            raise DatabaseError("No se pudo eliminar la publicación")

        return JSONResponse(content={"msg": "Publicación eliminada con éxito"}, status_code=200)

    except (NotFoundError, AuthorizationError, DatabaseError):
        raise
    except Exception as e:
        raise DatabaseError(f"Error al eliminar la publicación: {str(e)}") from e
