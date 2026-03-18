from celery import Celery

from config import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    include=[
        "tasks.tasks",
    ]
)
