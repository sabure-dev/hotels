from fastapi_mail import FastMail, MessageSchema

from .celery_app import celery_app
from ..config.settings import settings
from ..utils.jwt_utils import create_email_verification_token

conf = FastMail(settings.smtp)


@celery_app.task
def send_email_async(subject: str, email_to: str, body: str):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype="html"
    )
    conf.send_message(message)


@celery_app.task
def send_verification_email_task(user_email: str):
    token = create_email_verification_token(user_email)
    verification_url = f"{settings.app.frontend_url}/verify-email?token={token}"

    email_body = f"""
    <p>Пожалуйста, подтвердите ваш email, перейдя по ссылке:</p>
    <p><a href="{verification_url}">{verification_url}</a></p>
    <p>Если вы не запрашивали подтверждение email, проигнорируйте это письмо.</p>
    """

    send_email_async.delay(
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

    send_email_async.delay(
        "Сброс пароля",
        user_email,
        email_body
    )
