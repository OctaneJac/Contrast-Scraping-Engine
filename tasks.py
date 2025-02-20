import logging
from celery.utils.log import get_task_logger
from celery_config import celery_app
import time
import asyncio
from validation_scrapers.validation_scraper import run_store_validation
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
from spider_loader import get_all_spiders
import subprocess

# for debugging purposes
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)  # Set logging level to INFO
handler = logging.FileHandler('my_log.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#Dummy Task
@celery_app.task(name='tasks.apiworld')
def apiworld():
    logger.info('Demo task started!')
    time.sleep(10)  # Simulate a task that takes 10 seconds to complete
    logger.info('Demo task completed!')
    return 'Demo task completed!'


# Spiders ##########################
@celery_app.task(name='tasks.run_spider', ignore_result=True)
def run_spider(spider_name):
    """ Runs a single Scrapy spider using subprocess """
    logger.info(f"Running spider: {spider_name}")
    try:
        result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            cwd="scraper_archive",  # Path to the Scrapy project
            capture_output=True,
            text=True
        )
        logger.info(f"Spider {spider_name} completed with output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Spider {spider_name} failed with error: {e.stderr}")
    return f"Spider {spider_name} completed."

@celery_app.task(name='tasks.run_all_scrapers', ignore_result=True)
def run_all_scrapers():
    logger.info("Running all spiders...")
    spiders = get_all_spiders()
    logger.info(f"Found spiders: {spiders}")
    for spider_name in spiders:
        run_spider.apply_async(args=[spider_name])
    logger.info("All spiders have been queued for execution.")


#/////////////////////////////////////////////////////////////////////////
# Validation Scraper Task (Runs every midnight, updates products)
STORES = [
    "Fitted Shop",
    "Outfitters",
    # Add all 20 stores here
]

@celery_app.task(name='tasks.run_validation_scrapers')
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
