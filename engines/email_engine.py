from core.config import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType


class EmailEngine:
    @staticmethod
    async def send_reset_password_email(email: str, token: str):
        reset_link = f"{settings.frontend_domain_name}/password-reset?token={token}"
        config = ConnectionConfig(
            MAIL_USERNAME="info.neomarketplace@gmail.com",
            MAIL_PASSWORD="savt gkkk tjkk yuee",
            MAIL_FROM="info.neomarketplace@gmail.com",
            MAIL_SERVER='smtp.gmail.com',
            MAIL_PORT=465,
            MAIL_SSL_TLS=True,
            MAIL_STARTTLS=False,
        )
        message = MessageSchema(
            subject="Sirius Account: Password Reset Request",
            recipients=[email],
            body=f"Click the link to reset your password: {reset_link}",
            subtype=MessageType.html,
        )
        fm = FastMail(config)
        await fm.send_message(message)
