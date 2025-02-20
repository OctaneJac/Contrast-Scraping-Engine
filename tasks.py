import logging
from celery.utils.log import get_task_logger
from celery_config import celery_app
import time

# for debugging purposes
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)  # Set logging level to INFO
handler = logging.FileHandler('my_log.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# the task itself
@celery_app.task(name='tasks.apiworld')
def apiworld():
    logger.info('Demo task started!')
    time.sleep(10)  # Simulate a task that takes 10 seconds to complete
    logger.info('Demo task completed!')
    return 'Demo task completed!'

@celery_app.task(name='tasks.run_scrapers')
def run_scrapers():
    logger.info('Starting all scrapers...')
    for scraper in ["scraper1", "scraper2", "scraper3"]:  # Replace with actual scrapers
        logger.info(f"Running {scraper}...")
        time.sleep(2)  # Simulate scraper execution
    logger.info('All scrapers completed.')
    return "Scrapers Done"

# Validation Scraper Task (Runs every midnight)
@celery_app.task(name='tasks.run_validation_scrapers')
def run_validation_scrapers():
    logger.info('Starting validation scrapers...')
    for site in ["site1.com", "site2.com", "site3.com"]:  # Replace with actual sites
        logger.info(f"Validating {site}...")
        time.sleep(2)
    logger.info('Validation complete.')
    return "Validation Done"
