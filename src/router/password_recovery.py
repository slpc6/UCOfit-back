"""Router para la recuperación de contraseña"""

import secrets
from datetime import datetime, timedelta, timezone
import os
import bcrypt

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from model.password_recovery import (
    PasswordRecoveryRequest,
    PasswordResetRequest,
    TokenValidationResponse,
)
from services.email_service import email_service
from util.load_data import get_mongo_data, get_secrets
from exceptions.custom_exceptions import DatabaseError, EmailError


router = APIRouter(prefix="/password-recovery", tags=["password-recovery"])
DATA = get_mongo_data()
DATA_TOKEN = get_mongo_data('recovery_tokens')
SECRET_KEY, ALGORITHM = get_secrets()
RECOVERY_TOKENS = "recovery_tokens"
FRONTEND_URL = os.getenv("FRONTEND_URL")


@router.post("/request")
async def request_password_recovery(request: PasswordRecoveryRequest) -> JSONResponse:
    """
    Solicita la recuperación de contraseña enviando un email

    Args:
        request: Datos de la solicitud de recuperación

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:

        user = DATA.find_one({"email": request.email})
        if not user:

            return JSONResponse(
                status_code=200,
                content={
                    "msg": "Si el correo existe, recibirás un email para resetear la contraseña."
                },
            )

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        token_data = {
            "email": request.email,
            "token": token,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now(timezone.utc),
        } 
        DATA_TOKEN.insert_one(token_data)

        email_sent = await email_service.send_password_recovery_email(
            email=request.email, token=token, frontend_url=FRONTEND_URL
        )

        if not email_sent:
            DATA_TOKEN.delete_one({"token": token})
            raise EmailError("Error al enviar el email de recuperación.")

        return JSONResponse(
            status_code=200,
            content={"msg": "Si el correo existe, recibirás un email para resetear la contraseña."},
        )

    except Exception as e:
        raise DatabaseError(f"Error al solicitar la recuperación de contraseña: {str(e)}") from e


@router.get("/validate-token/{token}")
def validate_token(token: str) -> TokenValidationResponse:
    """
    Valida si un token de recuperación es válido

    Args:
        token: Token a validar

    Returns:
        TokenValidationResponse: Resultado de la validación
    """
    try:

        token_data = DATA_TOKEN.find_one({"token": token})

        if not token_data:
            return TokenValidationResponse(valid=False, msg="Token no encontrado")

        if token_data.get("used", False):
            return TokenValidationResponse(valid=False, msg="Token ya utilizado")

        expires_at = token_data.get("expires_at")
        if expires_at:

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)

            if current_time > expires_at:
                return TokenValidationResponse(valid=False, msg="Token expirado")

        return TokenValidationResponse(valid=True, msg="Token válido")

    except Exception as e:
        raise DatabaseError(f"Error al validar el token: {str(e)}") from e


@router.post("/reset")
async def reset_password(request: PasswordResetRequest) -> JSONResponse:
    """
    Resetea la contraseña usando un token válido

    Args:
        request: Datos para resetear la contraseña

    Returns:
        JSONResponse: Respuesta de la API
    """
    try:

        token_validation = validate_token(request.token)
        if not token_validation.valid:
            return JSONResponse(status_code=400, content={"msg": token_validation.msg})

        token_data = DATA_TOKEN.find_one({"token": request.token})
        if not token_data:
            return JSONResponse(status_code=400, content={"msg": "Token no encontrado"})

        if len(request.new_password) < 8:
            return JSONResponse(
                status_code=400, content={"msg": "La contraseña debe tener al menos 8 caracteres"}
            )

        user = DATA.find_one({"email": token_data["email"]})
        if not user:
            return JSONResponse(status_code=404, content={"msg": "Usuario no encontrado"})

        hashed_password = bcrypt.hashpw(request.new_password.encode("utf-8"), bcrypt.gensalt())

        DATA.update_one({"email": token_data["email"]}, {"$set": {"password": hashed_password}})

        DATA_TOKEN.update_one(
            {"token": request.token},
            {"$set": {"used": True, "used_at": datetime.now(timezone.utc)}},
        )

        await email_service.send_password_reset_confirmation(token_data["email"])

        return JSONResponse(status_code=200, content={"msg": "Contraseña actualizada exitosamente"})

    except Exception as e:
        raise DatabaseError(f"Error al resetear la contraseña: {str(e)}") from e
