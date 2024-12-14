from celery import Celery
from core.config import settings

celery_app = Celery(
    'auth_tasks',
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=['core.tasks']
)

celery_app.conf.task_routes = {
    "core.tasks.*": {"queue": "emails"},
}

import core.tasks
