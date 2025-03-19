from pydantic import BaseModel


class Comentario(BaseModel):
    usuario_id: str
    comentario: str
    fecha: str
    