from celery.schedules import crontab
from celery_config import celery_app
from celery import chain

celery_app.conf.beat_schedule = {
    'run_validation_scrapers': {
        'task': 'tasks.run_validation_scrapers',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
        # 'options': {'queue': 'validation_queue'},
    },
}

# Chain Data Migration after Scrapers Complete
@celery_app.task(name='tasks.run_scraper_chain')
def run_scraper_chain():
    return chain(
        celery_app.signature('tasks.run_all_scrapers'),
        celery_app.signature('tasks.run_migration')
    )()

celery_app.conf.beat_schedule['run_scraper_chain'] = {
    'task': 'tasks.run_scraper_chain',
    'schedule': crontab(hour=0, minute=0, day_of_week=0),  # Run every Sunday at midnight
}
