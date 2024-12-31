from celery import Celery

from ..config.settings import settings

celery_app = Celery(
    "users-api",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["core.tasks.email"]
)
