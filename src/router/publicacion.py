"""Modulo para la gestion de los endpoints relaciondos con publicaciones"""

from datetime import datetime
from typing import Optional
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from gridfs import GridFS
from bson.objectid import ObjectId


from router.usuario import datos_usuario
from util.load_data import get_mongo_data


router = APIRouter(prefix="/publicacion", tags=["Publicacion"])


def convertir_fechas_a_string(doc):
    """Convierte todas las fechas datetime a string en un documento"""
    if isinstance(doc, dict):
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
            elif isinstance(value, list):
                for item in value:
                    convertir_fechas_a_string(item)
            elif isinstance(value, dict):
                convertir_fechas_a_string(value)
    elif isinstance(doc, list):
        for item in doc:
            convertir_fechas_a_string(item)
    return doc


@router.post("/crear")
def crear_publicacion(
    titulo: str = Form(...),
    descripcion: str = Form(...),
    video: UploadFile = File(...),
    usuario: dict = Depends(datos_usuario)
) -> JSONResponse:
    """Crea una nueva publicación en la base de datos

    :args:
    - titulo: título de la publicación.
    - descripcion: descripción de la publicación.
    - video: archivo de video enviado como multipart/form-data.
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    try:
        collection = get_mongo_data('publicacion')

        db = collection.database
        fs = GridFS(db)
        file_id = fs.put(
            video.file,
            filename=video.filename,
            content_type=video.content_type or "video/mp4",
        )

        publicacion_doc = {
            "titulo": titulo,
            "descripcion": descripcion,
            "video": str(file_id),
            "usuario_id": usuario["email"],
            "comentarios": [],
            "puntuacion": 0
        }

        result = collection.insert_one(publicacion_doc)

        return JSONResponse(
            content={
                "msg": "Publicación creada con éxito",
                "publicacion_id": str(result.inserted_id),
                "video_id": str(file_id)
            },
            status_code=201
        )
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al crear la publicación: {e}"}, status_code=500
        )


@router.get("/general")
def listar_publicaciones(usuario: dict = Depends(datos_usuario)):
    """Lista todas las publicaciones disponibles con URLs de video integradas

    :args:
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con la lista de publicaciones y URLs de video.
    """
    try:
        collection = get_mongo_data('publicacion')
        publicaciones = list(collection.find())
        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])
            if "video" in pub and isinstance(pub["video"], str):
                video_id = str(pub["video"])
                pub["video_url"] = f"http://localhost:8000/publicacion/video/{video_id}"
                pub["video"] = video_id
            
            # Convertir todas las fechas a string
            convertir_fechas_a_string(pub)

        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al listar publicaciones: {e}"}, status_code=500
        )


@router.get("/video/{video_id}")
def obtener_video_endpoint(video_id: str):
    """Devuelve el stream del video almacenado en GridFS por su id"""
    try:
        collection = get_mongo_data('publicacion')
        db = collection.database
        fs = GridFS(db)
        grid_out = fs.get(ObjectId(video_id))

        def iterfile():
            chunk = grid_out.read(1024 * 1024)
            while chunk:
                yield chunk
                chunk = grid_out.read(1024 * 1024)

        media_type = getattr(grid_out, 'content_type', 'application/octet-stream') or 'application/octet-stream'
        return StreamingResponse(iterfile(), media_type=media_type)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al obtener el video: {e}"}, status_code=500
        )


@router.get("/usuario")
def listar_publicaciones_usuario(usuario: dict = Depends(datos_usuario)):
    """Lista todas las publicaciones de un usuario específico con URLs de video integradas

    :args:
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con la lista de publicaciones del usuario y URLs de video.
    """
    try:
        collection = get_mongo_data('publicacion')
        publicaciones = list(collection.find({"usuario_id": usuario["email"]}))

        for pub in publicaciones:
            if "_id" in pub:
                pub["_id"] = str(pub["_id"])
            if "video" in pub and isinstance(pub["video"], str):
                video_id = str(pub["video"])
                pub["video_url"] = f"http://localhost:8000/publicacion/video/{video_id}"
                pub["video"] = video_id
            
            # Convertir todas las fechas a string
            convertir_fechas_a_string(pub)

        return JSONResponse(content={"publicaciones": publicaciones}, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al listar publicaciones del usuario: {e}"},
            status_code=500,
        )


@router.get("/{publicacion_id}")
def obtener_publicacion(publicacion_id: str):
    """Devuelve una publicacion filtrada por id

    :args:
    - publicacion_id: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con la publicacion encontrada.
    """
    try:
        collection = get_mongo_data('publicacion')
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            return JSONResponse(content={"msg": "Publicacion no encontrada"}, status_code=404)
        
        publicacion["_id"] = str(publicacion["_id"])
        
        # Convertir todas las fechas a string
        convertir_fechas_a_string(publicacion)

        return JSONResponse(content=publicacion, status_code=200)
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al listar publicaciones del usuario: {e}"},
            status_code=500,
        )


@router.put("/editar/{publicacion_id}")
def editar_publicacion(
    publicacion_id: str,
    titulo: Optional[str] = None,
    descripcion: Optional[str] = None,
    usuario: dict = Depends(datos_usuario),
):
    """Actualiza una publicación existente

    :args:
    - publicacion_id: id de la publicación a editar.
    - titulo: nuevo título (opcional).
    - descripcion: nueva descripción (opcional).
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    try:
        collection = get_mongo_data('publicacion')
        
        # Verificar que la publicación existe
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            return JSONResponse(
                content={"msg": "Publicación no encontrada"}, 
                status_code=404
            )
        
        # Verificar permisos - solo el autor puede editar
        if publicacion.get("usuario_id") != usuario["email"]:
            return JSONResponse(
                content={"msg": "No tienes permiso para editar esta publicación"},
                status_code=403,
            )
        
        # Construir datos de actualización
        update_data = {}
        if titulo is not None:
            update_data["titulo"] = titulo
        if descripcion is not None:
            update_data["descripcion"] = descripcion
        
        # Verificar que hay datos para actualizar
        if not update_data:
            return JSONResponse(
                content={"msg": "No se proporcionaron datos para actualizar"},
                status_code=400,
            )
        
        # Actualizar la publicación
        result = collection.update_one(
            {"_id": ObjectId(publicacion_id)}, 
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return JSONResponse(
                content={"msg": "No se realizaron cambios en la publicación"},
                status_code=200
            )
        
        return JSONResponse(
            content={"msg": "Publicación actualizada con éxito"}, 
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al editar la publicación: {e}"}, 
            status_code=500
        )

@router.delete("/eliminar/{publicacion_id}")
def eliminar_publicacion(
    publicacion_id: str, 
    usuario: dict = Depends(datos_usuario)
):
    """Elimina una publicación existente

    :args:
    - publicacion_id: id de la publicación a eliminar.
    - usuario: datos del usuario autenticado.

    :Returns:
    - Un JSONResponse con mensaje de éxito o error.
    """
    try:
        collection = get_mongo_data('publicacion')
        
        # Verificar que la publicación existe
        publicacion = collection.find_one({"_id": ObjectId(publicacion_id)})
        if not publicacion:
            return JSONResponse(
                content={"msg": "Publicación no encontrada"}, 
                status_code=404
            )
        
        # Verificar permisos - solo el autor puede eliminar
        if publicacion.get("usuario_id") != usuario["email"]:
            return JSONResponse(
                content={"msg": "No tienes permiso para eliminar esta publicación"},
                status_code=403,
            )
        
        # Eliminar el video de GridFS si existe
        if "video" in publicacion and publicacion["video"]:
            try:
                db = collection.database
                fs = GridFS(db)
                fs.delete(ObjectId(publicacion["video"]))
            except Exception as e:
                # Log el error pero continúa con la eliminación de la publicación
                print(f"Error al eliminar video de GridFS: {e}")
        
        # Eliminar la publicación
        result = collection.delete_one({"_id": ObjectId(publicacion_id)})
        
        if result.deleted_count == 0:
            return JSONResponse(
                content={"msg": "No se pudo eliminar la publicación"},
                status_code=500
            )
        
        return JSONResponse(
            content={"msg": "Publicación eliminada con éxito"}, 
            status_code=200
        )
        
    except Exception as e:
        return JSONResponse(
            content={"msg": f"Error al eliminar la publicación: {e}"}, 
            status_code=500
        )
