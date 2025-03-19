from pydantic import BaseModel
from models.model_comentario import Comentario

class Publicacion(BaseModel):
    titulo: str
    descripcion: str
    video: str
    usuario_id: str
    comentarios: list[Comentario | None] 
    puntuacion: int
