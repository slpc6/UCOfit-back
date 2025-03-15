from pydantic import BaseModel

from models.model_usuario import Usuario

class Comentario(BaseModel):
    usuario: Usuario
    comentario: str
    fecha: str
    