from celery import Celery
import os

celery_app = Celery(
    'main',
    broker=os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://localhost:6379/0")
)
celery_app.autodiscover_tasks(['tasks'])  # Adjust with the actual name of your tasks module if necessary

# Task routing
celery_app.conf.task_routes = {}

# Celery configuration for Flower and persistence
celery_app.conf.update(
    result_expires=3600,  # Increased to 1 hour for longer task visibility (adjust as needed)
    task_track_started=True,  # Track when tasks start
    task_send_sent_event=True,  # Send events when tasks are sent
    worker_send_task_events=True,  # Ensure workers send task events
)

import tasks  # Import tasks module to register tasks
import celerybeat_schedule
# from celerysignals import * 

# Check Redis connection
with celery_app.connection() as connection:
    connection.ensure_connection()
    print("Connected to Redis successfully")