from celery.schedules import crontab
from celery_config import celery_app
from celery import chain

celery_app.conf.beat_schedule = {
    'run_scrapers_every_sunday': {
        'task': 'tasks.run_scrapers',
        'schedule': crontab(minute=0, hour=0, day_of_week='sun'),  # Every Sunday at midnight
        'options': {'queue': 'scraper_queue'},
    },
    'run_validation_scrapers_midnight': {
        'task': 'tasks.run_validation_scrapers',
        'schedule': crontab(minute=0, hour=0),  # Every day at midnight
        'options': {'queue': 'validation_queue'},
    },
}

# # Chain Data Migration after Scrapers Complete
# @celery_app.task(name='tasks.run_scraper_chain')
# def run_scraper_chain():
#     return chain(run_scrapers.s(), data_migration.s())()
