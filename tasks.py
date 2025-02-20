import logging
from celery.utils.log import get_task_logger
from celery_config import celery_app
import time
import asyncio
from validation_scrapers.validation_scraper import run_store_validation

# for debugging purposes
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)  # Set logging level to INFO
handler = logging.FileHandler('my_log.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#Dummy Tasks
@celery_app.task(name='tasks.apiworld')
def apiworld():
    logger.info('Demo task started!')
    time.sleep(10)  # Simulate a task that takes 10 seconds to complete
    logger.info('Demo task completed!')
    return 'Demo task completed!'

#Run main spiders
@celery_app.task(name='tasks.run_scrapers')
def run_scrapers():
    logger.info('Starting all scrapers...')
    for scraper in ["scraper1", "scraper2", "scraper3"]:  # Replace with actual scrapers
        logger.info(f"Running {scraper}...")
        time.sleep(2)  # Simulate scraper execution
    logger.info('All scrapers completed.')
    return "Scrapers Done"

# Validation Scraper Task (Runs every midnight, updates products)
STORES = [
    "Fitted Shop",
    "Outfitters",
    # Add all 20 stores here
]

@celery_app.task
def validate_all_stores():
    """Run validation scrapers for all stores in parallel"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_all_validations())

async def run_all_validations():
    """Run each store's scraper concurrently using asyncio"""
    tasks = [run_store_validation(store_name) for store_name in STORES]
    print("Async running validation scrapers...")
    await asyncio.gather(*tasks)  # Runs all store scrapers in parallel
