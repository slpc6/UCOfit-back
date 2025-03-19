from pydantic import BaseModel

from models.model_usuario import Usuario
class Puntuacion(BaseModel):
    usuario_id: str
    puntuacion: int
    