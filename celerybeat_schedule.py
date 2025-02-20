from celery.schedules import crontab
from celery_config import celery_app
from celery import chain

celery_app.conf.beat_schedule = {
    'run_scrapers_debug': {
        'task': 'tasks.run_scrapers',
        'schedule': 10.0,  # Run every 10 seconds for debugging
        # 'options': {'queue': 'scraper_queue'},
    },
    'run_validation_scrapers_debug': {
        'task': 'tasks.run_validation_scrapers',
        'schedule': 10.0,  # Run every 10 seconds for debugging
        # 'options': {'queue': 'validation_queue'},
    },
}

# # Chain Data Migration after Scrapers Complete
# @celery_app.task(name='tasks.run_scraper_chain')
# def run_scraper_chain():
#     return chain(run_scrapers.s(), data_migration.s())()
