from app.tasks import celery

# Required for celery to discover tasks in tasks.py
celery.autodiscover_tasks(['app'])
