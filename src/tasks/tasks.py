from time import sleep

from .celery_app import celery_app


@celery_app.task
def test_task():
    sleep(5)
    print("Я молодец")