"""Servicio de email para recuperación de contraseña."""

import os

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

from exceptions.custom_exceptions import EmailError

load_dotenv()


class EmailService:
    """Servicio para el envío de emails con soporte para Gmail y SendGrid."""

    def __init__(self):
        """Inicializa el servicio de email con configuración desde variables de entorno."""
        # Configuración del proveedor de email
        mail_provider = os.getenv("MAIL_PROVIDER", "sendgrid").lower()

        if mail_provider == "gmail":
            # Configuración para Gmail
            username = os.getenv("GMAIL_USERNAME")
            password = os.getenv("GMAIL_APP_PASSWORD")

            self.config = ConnectionConfig(
                MAIL_USERNAME=username,
                MAIL_PASSWORD=password,
                MAIL_FROM=username,
                MAIL_PORT=465,
                MAIL_SERVER="smtp.gmail.com",
                MAIL_STARTTLS=False,
                MAIL_SSL_TLS=True,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                TIMEOUT=60,
            )
        else:
            # Configuración para SendGrid (por defecto)
            sendgrid_username = os.getenv("SENDGRID_USERNAME", "apikey")
            sendgrid_password = os.getenv("SENDGRID_API_KEY")
            sendgrid_from = os.getenv("SENDGRID_FROM_EMAIL")
            
            self.config = ConnectionConfig(
                MAIL_USERNAME=sendgrid_username,
                MAIL_PASSWORD=sendgrid_password,
                MAIL_FROM=sendgrid_from,
                MAIL_PORT=587,
                MAIL_SERVER="smtp.sendgrid.net",
                MAIL_STARTTLS=True,
                MAIL_SSL_TLS=False,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                TIMEOUT=60,
            )

        self.template_env = Environment(loader=FileSystemLoader("src/templates"))

        self.fastmail = FastMail(self.config)

    async def send_password_recovery_email(self, email: str, token: str, frontend_url: str) -> bool:
        """Envía email de recuperación de contraseña.

        Args:
            email: Correo del usuario
            token: Token de recuperación
            frontend_url: URL del frontend para el enlace

        Returns:
            bool: True si se envió correctamente, False en caso contrario

        Raises:
            EmailError: Si hay error enviando el email
        """
        try:

            recovery_link = f"{frontend_url}/resetar-contrasena?token={token}"

            template = self.template_env.get_template("password_recovery.html")
            html_content = template.render(recovery_link=recovery_link, user_email=email)

            message = MessageSchema(
                subject="Recuperación de Contraseña - UCOfit",
                recipients=[email],
                body=html_content,
                subtype="html",
            )

            await self.fastmail.send_message(message)
            return True

        except Exception as e:
            raise EmailError(f"Error enviando email de recuperación: {str(e)}") from e

    async def send_password_reset_confirmation(self, email: str) -> bool:
        """Envía email de confirmación de cambio de contraseña.

        Args:
            email: Correo del usuario

        Returns:
            bool: True si se envió correctamente, False en caso contrario

        Raises:
            EmailError: Si hay error enviando el email
        """
        try:

            template = self.template_env.get_template("password_reset_confirmation.html")
            html_content = template.render(user_email=email)

            message = MessageSchema(
                subject="Contraseña Actualizada - UCOfit",
                recipients=[email],
                body=html_content,
                subtype="html",
            )

            await self.fastmail.send_message(message)
            return True

        except Exception as e:
            raise EmailError(f"Error enviando email de confirmación: {str(e)}") from e


email_service = EmailService()
