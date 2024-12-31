from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class DatabaseSettings(BaseSettings):
    url: str
    echo: bool = False

    model_config = SettingsConfigDict(env_prefix='DATABASE_')


class SMTPSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str
    from_email: str
    email_verification_secret_key: str
    email_verification_algorithm: str = "HS256"
    email_verification_expire_minutes: int = 60

    model_config = SettingsConfigDict(env_prefix='SMTP_')


class CORSSettings(BaseSettings):
    origins: List[str]

    model_config = SettingsConfigDict(env_prefix='CORS_')


class CelerySettings(BaseSettings):
    broker_url: str
    result_backend: str

    model_config = SettingsConfigDict(env_prefix='CELERY_')


class AppSettings(BaseSettings):
    frontend_url: str

    model_config = SettingsConfigDict(env_prefix='APP_')


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    smtp: SMTPSettings = SMTPSettings()
    cors: CORSSettings = CORSSettings()
    celery: CelerySettings = CelerySettings()
    app: AppSettings = AppSettings()


settings = Settings()
