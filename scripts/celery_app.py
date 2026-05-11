from celery import Celery

celery = Celery(
    "scripts.worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["scripts.worker"]
)

celery.conf.update(
    broker_connection_retry_on_startup=True
)