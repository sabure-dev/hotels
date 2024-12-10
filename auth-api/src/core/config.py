import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent

load_dotenv()


class DbSettings(BaseModel):
    db_host: str = os.getenv('DB_HOST')
    db_port: str = os.getenv('DB_PORT')
    db_name: str = os.getenv('DB_NAME')
    db_user: str = os.getenv('DB_USER')
    db_pass: str = os.getenv('DB_PASS')


class AuthJWTSettings(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = os.environ.get("ALGORITHM")
    access_token_expire_minutes: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS")


class SMTPSettings(BaseModel):
    smtp_user: str = os.environ.get("SMTP_USER")
    smtp_pass: str = os.environ.get("SMTP_PASS")

    reset_password_token_expire_minutes: int = int(os.environ.get("RESET_PASSWORD_TOKEN_EXPIRE_MINUTES"))
    reset_password_email_template: str = os.environ.get("RESET_PASSWORD_EMAIL_TEMPLATE")
    reset_password_secret_key: str = os.environ.get("RESET_PASSWORD_SECRET_KEY")
    reset_password_algorithm: str = os.environ.get("RESET_PASSWORD_ALGORITHM")

    email_verification_token_expire_hours: int = int(os.environ.get("EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS"))
    email_verification_email_template: str = os.environ.get("EMAIL_VERIFICATION_EMAIL_TEMPLATE")
    email_verification_secret_key: str = os.environ.get("EMAIL_VERIFICATION_SECRET_KEY")
    email_verification_algorithm: str = os.environ.get("EMAIL_VERIFICATION_ALGORITHM")


class Settings(BaseSettings):
    db: DbSettings = DbSettings()
    smtp: SMTPSettings = SMTPSettings()
    auth_jwt: AuthJWTSettings = AuthJWTSettings()


settings = Settings()
