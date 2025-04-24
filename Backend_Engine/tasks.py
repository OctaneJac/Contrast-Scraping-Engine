import logging
from celery.utils.log import get_task_logger
from Backend_Engine.celery_config import celery_app
import time
import asyncio
# from tasks.validation_scraper import run_store_validation
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import logging
import subprocess
from datetime import datetime, timedelta


# for debugging purposes
logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)  # Set logging level to INFO
handler = logging.FileHandler('my_log.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
import os, dotenv
import psycopg2

dotenv.load_dotenv()  # Load environment variables from .env file
postgres_url = os.environ.get("POSTGRES_URI")

# Spiders ##########################
@celery_app.task(name='tasks.run_spider', bind=True, ignore_result=True, max_retries=3)
def run_spider(self, spider_id):
    """Run a Scrapy spider and log run details."""
    
    celery_trigger_time = datetime.utcnow()
    
    conn = psycopg2.connect(postgres_url)
    cursor = conn.cursor()

    # Fetch the scraper name using the ID
    cursor.execute("SELECT name FROM listofscrapers WHERE id = %s", (spider_id,))
    result = cursor.fetchone()
    logger.info(f"Runnning spider {result} with ID {spider_id}")

    if not result:
        logger.error(f"No scraper found with ID {spider_id}")
        return

    spider_name = result[0]
    logger.info(f"Running spider: {spider_name}")
    actual_start_time = datetime.utcnow()

    try:
        run_result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            cwd="scraper_archive",
            capture_output=True,
            text=True,
            check=True
        )
        end_time = datetime.utcnow()
        duration = int((end_time - actual_start_time).total_seconds())

        # Insert log if successful
        cursor.execute(
            """
            INSERT INTO spider_logs (
                scraper_id, scraper_name, celery_trigger_time,
                actual_start_time, end_time, duration_seconds, retries, result
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                spider_id, spider_name, celery_trigger_time,
                actual_start_time, end_time, duration,
                self.request.retries, run_result.stdout[:10000]
            )
        )

        # Update last ran on listofscrapers
        cursor.execute(
            """
            UPDATE listofscrapers
            SET last_ran = %s
            WHERE id = %s
            """,
            (end_time, spider_id,)
        )

        conn.commit()
        logger.info(f"Spider {spider_name} completed successfully.")

    except subprocess.CalledProcessError as e:
        end_time = datetime.utcnow()
        duration = int((end_time - actual_start_time).total_seconds())

        # Insert failed log
        cursor.execute(
            """
            INSERT INTO spider_logs (
                scraper_id, scraper_name, celery_trigger_time,
                actual_start_time, end_time, duration_seconds, retries, error
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (   
                spider_id, spider_name, celery_trigger_time,
                actual_start_time, end_time, duration,
                self.request.retries, e.stderr[:10000]
            )
        )

        # Optional: mark scraper status as 'raising warnings' or 'broken' depending on retry count
        if self.request.retries >= self.max_retries:
            new_status = 'broken'
        else:
            new_status = 'raising warnings'

        cursor.execute(
            """
            UPDATE listofscrapers
            SET status = %s, 
            WHERE id = %s
            """,
            (new_status, end_time, spider_id,)
        )

        conn.commit()
        logger.error(f"Spider {spider_name} failed: {e.stderr}")

    finally:
        cursor.close()
        conn.close()

@celery_app.task(name='tasks.run_all_scrapers', ignore_result=True)
def run_all_scrapers():
    logger.info("Running all spiders...")
    for spider_id in range(1,4):
        run_spider.apply_async(args=[spider_id])
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




