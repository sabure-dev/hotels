import smtplib
from email.mime.text import MIMEText
from core.celery_app import celery_app
from core.config import settings


@celery_app.task
def send_verification_email_task(email: str, verification_url: str):
    msg = MIMEText(settings.smtp.email_verification_email_template.format(verification_url=verification_url))
    msg['Subject'] = 'Подтверждение email'
    msg['From'] = settings.smtp.smtp_user
    msg['To'] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.smtp.smtp_user, settings.smtp.smtp_pass)
        smtp.send_message(msg)


@celery_app.task
def send_password_reset_email_task(email: str, reset_url: str):
    msg = MIMEText(settings.smtp.reset_password_email_template.format(reset_url=reset_url))
    msg['Subject'] = 'Восстановление пароля'
    msg['From'] = settings.smtp.smtp_user
    msg['To'] = email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(settings.smtp.smtp_user, settings.smtp.smtp_pass)
        smtp.send_message(msg)
