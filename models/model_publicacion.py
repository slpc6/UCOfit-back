from pydantic import BaseModel

from bson.objectid import ObjectId

class Publicacion(BaseModel):
    titulo: str
    descripcion: str
    video: str
    usuario_id: str
    comentarios: dict
    puntuacion: int
