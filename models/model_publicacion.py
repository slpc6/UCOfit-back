from pydantic import BaseModel


class Publicacion(BaseModel):
    titulo: str
    descripcion: str
    video: str
    usuario_id: str
    comentarios: dict
    puntuacion: int
