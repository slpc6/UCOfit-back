"""Endpoint para verificar el estado del sevicio"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/healthz")


@router.get(path="/")
def healthz() -> JSONResponse:
    """Endpoint para verificar el estado del servicio
    Return:
    - Un JSONResponse con un mensaje de OK si el servicio funciona
    correctamente.

    """
    return JSONResponse(status_code=200, content={"msg": "OK"})
