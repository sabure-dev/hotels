from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import logging
import asyncio

from .celery_app import celery_app
from ..config.settings import settings
from ..utils.jwt_utils import create_email_verification_token


logger = logging.getLogger(__name__)

smtp_config = ConnectionConfig(
    MAIL_USERNAME=settings.smtp.username,
    MAIL_PASSWORD=settings.smtp.password,
    MAIL_FROM=settings.smtp.from_email,
    MAIL_PORT=settings.smtp.port,
    MAIL_SERVER=settings.smtp.host,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(smtp_config)


def send_email_sync(subject: str, email_to: str, body: str):
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype="html"
        )
        logger.info(f"Attempting to send email to {email_to}")
        # Создаем новый event loop для асинхронной отправки
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(fastmail.send_message(message))
            logger.info(f"Successfully sent email to {email_to}")
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Failed to send email to {email_to}: {str(e)}")
        raise


@celery_app.task
def send_verification_email_task(user_email: str):
    token = create_email_verification_token(user_email)
    verification_url = f"{settings.app.frontend_url}/verify-email?token={token}"

    email_body = f"""
    <p>Пожалуйста, подтвердите ваш email, перейдя по ссылке:</p>
    <p><a href="{verification_url}">{verification_url}</a></p>
    <p>Если вы не запрашивали подтверждение email, проигнорируйте это письмо.</p>
    """

    send_email_sync(
        "Подтверждение email",
        user_email,
        email_body
    )


@celery_app.task
def send_password_reset_email_task(user_email: str):
    token = create_email_verification_token(user_email)
    reset_url = f"{settings.app.frontend_url}/reset-password?token={token}"

    email_body = f"""
    <p>Вы запросили сброс пароля.</p>
    <p>Для сброса пароля перейдите по ссылке:</p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>Если вы не запрашивали сброс пароля, проигнорируйте это письмо.</p>
    """

    send_email_sync(
        "Сброс пароля",
        user_email,
        email_body
    )
