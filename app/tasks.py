from app.config import create_app 
from celery import shared_task 
from time import sleep
from celery import group
import os   
import psycopg2
import subprocess
from pymongo import MongoClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

flask_app = create_app()  
celery_app = flask_app.extensions["celery"] 

# Load environment variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
POSTGRES_URI = os.getenv("POSTGRES_URI")

@shared_task
def run_spider_task(spider_name):
    """
    Runs a Scrapy spider asynchronously using Celery.
    """
    try:
        result = subprocess.run(
            ["scrapy", "crawl", spider_name],
            cwd="scraper_archive",  # Path to the Scrapy project
            capture_output=True,
            text=True
        )
        return {"status": "success", "output": result.stdout}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# @shared_task
# def fetch_mongo_data(batch_size=100):
#     """
#     Fetches scraped product data from MongoDB in batches and processes them asynchronously.
#     """
#     mongo_client = MongoClient(MONGO_URI)
#     mongo_db = mongo_client[MONGO_DB]
#     mongo_collection = mongo_db[MONGO_COLLECTION]

#     cursor = mongo_collection.find({}).batch_size(batch_size)
#     batch = []
#     records_processed = 0
#     tasks = []  # List to hold tasks for concurrent execution

#     for item in cursor:
#         if '_id' in item:
#             item['_id'] = str(item['_id'])

#         batch.append(item)
#         if len(batch) >= batch_size:
#             #logger.debug(batch)
#             tasks.append(process_product_data.s(batch))  # Create a signature for the task with batch as the only argument
#             batch = []
#             records_processed += batch_size

#     if batch:  # Process any remaining records
#         tasks.append(process_product_data.s(batch))
#         records_processed += len(batch)

#     # Execute all tasks in parallel
#     group(*tasks).apply_async()

#     mongo_client.close()
#     return f"Fetched {records_processed} records from MongoDB."

# def process_product_data(items):
#     """
#     Processes MongoDB data and inserts it into PostgreSQL efficiently using batch inserts.
#     """
#     pg_conn = psycopg2.connect(POSTGRES_URI)
#     pg_cursor = pg_conn.cursor()

#     store_insertions = []
#     product_insertions = []
#     price_insertions = []

#     for item in items:
#         try:
#             store_name = item.get("store")
#             product_name = item.get("name")
#             product_url = item.get("url")
#             price = float(item.get("price", 0))  # Default to 0 if missing
#             retrieved_on = datetime.now()

#             if not all([store_name, product_name, product_url]):
#                 continue

#             # Ensure the store exists or insert it if not already present
#             pg_cursor.execute("SELECT store_id FROM stores WHERE store_name = %s", (store_name,))
#             store_result = pg_cursor.fetchone()

#             if store_result is None:
#                 # Insert store only if it doesn't already exist, using ON CONFLICT DO NOTHING
#                 store_insertions.append((store_name, retrieved_on))
#             else:
#                 store_id = store_result[0]

#             # Ensure the product exists
#             pg_cursor.execute("SELECT product_id FROM products WHERE product_url = %s", (product_url,))
#             product_result = pg_cursor.fetchone()

#             if product_result is None:
#                 product_insertions.append((store_id, product_name, product_url))
#             else:
#                 product_id = product_result[0]

#             # Store price history
#             price_insertions.append((product_id, price, retrieved_on))

#         except Exception as e:
#             print(f"[ERROR] Failed to process item: {item}\n{e}")

#     # Bulk insert stores, using ON CONFLICT DO NOTHING to avoid duplicate insertions
#     if store_insertions:
#         pg_cursor.executemany(
#             "INSERT INTO stores (store_name, last_retrieved_on) VALUES (%s, %s) ON CONFLICT (store_name) DO NOTHING",
#             store_insertions
#         )

#     # Bulk insert products
#     if product_insertions:
#         pg_cursor.executemany(
#             "INSERT INTO products (store_id, product_name, product_url) VALUES (%s, %s, %s) RETURNING product_id",
#             product_insertions
#         )

#     # Bulk insert price history
#     if price_insertions:
#         pg_cursor.executemany(
#             "INSERT INTO product_prices (product_id, price, retrieved_on) VALUES (%s, %s, %s)",
#             price_insertions
#         )

#     pg_conn.commit()
#     pg_cursor.close()
#     pg_conn.close()

#     return f"Processed {len(items)} records."


# @shared_task
# def store_price_history(product_id, price, retrieved_on):
#     """
#     Stores price history for a product in PostgreSQL.
#     """
#     try:
#         pg_conn = psycopg2.connect(POSTGRES_URI)
#         pg_cursor = pg_conn.cursor()
#         pg_cursor.execute(
#             "INSERT INTO product_prices (product_id, price, retrieved_on) VALUES (%s, %s, %s)",
#             (product_id, price, retrieved_on),
#         )
#         pg_conn.commit()  # Commit after insertion
#         pg_cursor.close()
#         pg_conn.close()
#         return f"Inserted price {price} for product {product_id}"

#     except Exception as e:
#         # Log error with details
#         print(f"[ERROR] Failed to store price history for product {product_id}: {e}")
#         return str(e)

@shared_task(bind=True)
def migrate_data(self):
    try:
        # Connect to MongoDB
        mongo_client = MongoClient(MONGO_URI)
        mongo_db = mongo_client[MONGO_DB]
        mongo_collection = mongo_db[MONGO_COLLECTION]
        print("[INFO] Connected to MongoDB.")

        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(POSTGRES_URI)
        pg_cursor = pg_conn.cursor()
        print("[INFO] Connected to PostgreSQL.")

        # Fetch scraped data from MongoDB
        mongo_data = mongo_collection.find({})
        records_processed = 0

        for item in mongo_data:
            try:
                store_name = item.get("store")
                product_name = item.get("name")
                product_url = item.get("url")
                price = float(item.get("price", 0))  # Default to 0 if price is missing
                retrieved_on = datetime.now()

                if not all([store_name, product_name, product_url]):
                    print(f"[WARNING] Skipping record due to missing fields: {item}")
                    continue

                # 1. Ensure the store exists
                pg_cursor.execute("SELECT store_id FROM stores WHERE store_name = %s", (store_name,))
                store_result = pg_cursor.fetchone()

                if store_result is None:
                    pg_cursor.execute(
                        "INSERT INTO stores (store_name, last_retrieved_on) VALUES (%s, %s) RETURNING store_id",
                        (store_name, retrieved_on),
                    )
                    store_id = pg_cursor.fetchone()[0]
                    print(f"[INFO] Inserted new store: {store_name} (ID: {store_id})")
                else:
                    store_id = store_result[0]

                # 2. Ensure the product exists
                pg_cursor.execute("SELECT product_id FROM products WHERE product_url = %s", (product_url,))
                product_result = pg_cursor.fetchone()

                if product_result is None:
                    pg_cursor.execute(
                        "INSERT INTO products (store_id, product_name, product_url) VALUES (%s, %s, %s) RETURNING product_id",
                        (store_id, product_name, product_url),
                    )
                    product_id = pg_cursor.fetchone()[0]
                    print(f"[INFO] Inserted new product: {product_name} (ID: {product_id})")
                else:
                    product_id = product_result[0]

                # 3. Insert price history
                pg_cursor.execute(
                    "INSERT INTO product_prices (product_id, price, retrieved_on) VALUES (%s, %s, %s)",
                    (product_id, price, retrieved_on),
                )
                print(f"[INFO] Inserted price for product ID {product_id}: {price} at {retrieved_on}")

                records_processed += 1

            except Exception as e:
                print(f"[ERROR] Failed to process item: {item}\n{e}")

        # Commit changes
        pg_conn.commit()
        print(f"[SUCCESS] Migration completed. {records_processed} records processed.")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        self.retry(exc=e)

    finally:
        # Close connections
        if 'pg_cursor' in locals():
            pg_cursor.close()
        if 'pg_conn' in locals():
            pg_conn.close()
        if 'mongo_client' in locals():
            mongo_client.close()
        print("[INFO] Database connections closed.")