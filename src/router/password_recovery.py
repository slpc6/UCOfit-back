"""Router para la recuperación de contraseña"""

import secrets
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from model.password_recovery import (
    PasswordRecoveryRequest,
    PasswordResetRequest,
    TokenValidationResponse
)
from services.email_service import email_service
from util.load_data import get_mongo_data, get_secrets

router = APIRouter(prefix="/password-recovery", tags=["password-recovery"])
DATA = get_mongo_data()
SECRET_KEY, ALGORITHM = get_secrets()

# Colección para tokens de recuperación
RECOVERY_TOKENS = "recovery_tokens"


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
        # Verificar si el usuario existe
        user = DATA.find_one({"email": request.email})
        if not user:
            # Por seguridad, devolvemos el mismo mensaje aunque el usuario no exista
            return JSONResponse(
                status_code=200,
                content={"msg": "Si el correo existe en nuestro sistema, recibirás un email con las instrucciones"}
            )
        
        # Generar token único
        token = secrets.token_urlsafe(32)
        
        # Calcular fecha de expiración (1 hora)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Guardar token en la base de datos
        token_data = {
            "email": request.email,
            "token": token,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.now(timezone.utc)
        }
        
        DATA.insert_one(token_data)
        
        # Obtener URL del frontend desde variables de entorno
        frontend_url = "http://localhost:5173"  # Por defecto para desarrollo
        
        # Enviar email de recuperación
        email_sent = await email_service.send_password_recovery_email(
            email=request.email,
            token=token,
            frontend_url=frontend_url
        )
        
        if not email_sent:
            # Si falla el envío del email, eliminar el token
            DATA.delete_one({"token": token})
            return JSONResponse(
                status_code=500,
                content={"msg": "Error al enviar el email de recuperación"}
            )
        
        return JSONResponse(
            status_code=200,
            content={"msg": "Si el correo existe en nuestro sistema, recibirás un email con las instrucciones"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"msg": f"Error interno del servidor: {str(e)}"}
        )


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
        # Buscar el token en la base de datos
        token_data = DATA.find_one({"token": token})
        
        if not token_data:
            return TokenValidationResponse(
                valid=False,
                msg="Token no encontrado"
            )
        
        # Verificar si ya fue usado
        if token_data.get("used", False):
            return TokenValidationResponse(
                valid=False,
                msg="Token ya utilizado"
            )
        
        # Verificar si ha expirado
        expires_at = token_data.get("expires_at")
        if expires_at:
            # Asegurar que ambas fechas tengan timezone
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)
            
            if current_time > expires_at:
                return TokenValidationResponse(
                    valid=False,
                    msg="Token expirado"
                )
        
        return TokenValidationResponse(
            valid=True,
            msg="Token válido"
        )
        
    except Exception as e:
        return TokenValidationResponse(
            valid=False,
            msg=f"Error al validar el token: {str(e)}"
        )


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
        # Validar el token primero
        token_validation = validate_token(request.token)
        if not token_validation.valid:
            return JSONResponse(
                status_code=400,
                content={"msg": token_validation.msg}
            )
        
        # Buscar el token en la base de datos
        token_data = DATA.find_one({"token": request.token})
        if not token_data:
            return JSONResponse(
                status_code=400,
                content={"msg": "Token no encontrado"}
            )
        
        # Validar la nueva contraseña
        if len(request.new_password) < 8:
            return JSONResponse(
                status_code=400,
                content={"msg": "La contraseña debe tener al menos 8 caracteres"}
            )
        
        # Buscar el usuario
        user = DATA.find_one({"email": token_data["email"]})
        if not user:
            return JSONResponse(
                status_code=404,
                content={"msg": "Usuario no encontrado"}
            )
        
        # Encriptar la nueva contraseña
        hashed_password = bcrypt.hashpw(
            request.new_password.encode("utf-8"), 
            bcrypt.gensalt()
        )
        
        # Actualizar la contraseña del usuario
        DATA.update_one(
            {"email": token_data["email"]},
            {"$set": {"password": hashed_password}}
        )
        
        # Marcar el token como usado
        DATA.update_one(
            {"token": request.token},
            {"$set": {"used": True, "used_at": datetime.now(timezone.utc)}}
        )
        
        # Enviar email de confirmación
        await email_service.send_password_reset_confirmation(token_data["email"])
        
        return JSONResponse(
            status_code=200,
            content={"msg": "Contraseña actualizada exitosamente"}
        )
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"msg": f"Error interno del servidor: {str(e)}"}
        )
