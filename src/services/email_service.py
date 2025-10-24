"""Servicio de email para recuperación de contraseña"""

import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Servicio para el envío de emails"""
    
    def __init__(self):
        """Inicializa el servicio de email con configuración de Gmail"""
        self.config = ConnectionConfig(
            MAIL_USERNAME=os.getenv("GMAIL_USERNAME"),
            MAIL_PASSWORD=os.getenv("GMAIL_APP_PASSWORD"),
            MAIL_FROM=os.getenv("GMAIL_USERNAME"),
            MAIL_PORT=587,
            MAIL_SERVER="smtp.gmail.com",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        
        # Configurar Jinja2 para templates
        self.template_env = Environment(
            loader=FileSystemLoader('src/templates')
        )
        
        self.fastmail = FastMail(self.config)
    
    async def send_password_recovery_email(self, email: str, token: str, frontend_url: str) -> bool:
        """
        Envía email de recuperación de contraseña
        
        Args:
            email: Correo del usuario
            token: Token de recuperación
            frontend_url: URL del frontend para el enlace
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Generar enlace de recuperación
            recovery_link = f"{frontend_url}/resetar-contrasena?token={token}"
            
            # Renderizar template
            template = self.template_env.get_template('password_recovery.html')
            html_content = template.render(
                recovery_link=recovery_link,
                user_email=email
            )
            
            # Crear mensaje
            message = MessageSchema(
                subject="Recuperación de Contraseña - UCOfit",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            # Enviar email
            await self.fastmail.send_message(message)
            return True
            
        except Exception as e:
            print(f"Error enviando email de recuperación: {e}")
            return False
    
    async def send_password_reset_confirmation(self, email: str) -> bool:
        """
        Envía email de confirmación de cambio de contraseña
        
        Args:
            email: Correo del usuario
            
        Returns:
            bool: True si se envió correctamente, False en caso contrario
        """
        try:
            # Renderizar template
            template = self.template_env.get_template('password_reset_confirmation.html')
            html_content = template.render(user_email=email)
            
            # Crear mensaje
            message = MessageSchema(
                subject="Contraseña Actualizada - UCOfit",
                recipients=[email],
                body=html_content,
                subtype="html"
            )
            
            # Enviar email
            await self.fastmail.send_message(message)
            return True
            
        except Exception as e:
            print(f"Error enviando email de confirmación: {e}")
            return False


# Instancia global del servicio
email_service = EmailService()
