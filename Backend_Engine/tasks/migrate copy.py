import os
import psycopg2
from psycopg2.extras import execute_batch
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, AutoReconnect
from datetime import datetime
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import logging
import time
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Validate environment variables
if not all([MONGO_URI, MONGO_DB, MONGO_COLLECTION, POSTGRES_URI]):
    logger.error("One or more environment variables are missing.")
    exit(1)

# Validate MongoDB URI format
if not re.match(r'^mongodb\+srv://.+@.+\.mongodb\.net/.+\?.+$', MONGO_URI):
    logger.error(f"Invalid MONGO_URI format: {MONGO_URI}")
    exit(1)

def connect_mongo_with_retry(max_attempts=5, initial_delay=5):
    """Attempt to connect to MongoDB with retries and exponential backoff"""
    attempt = 1
    delay = initial_delay
    while attempt <= max_attempts:
        try:
            logger.info(f"Attempting MongoDB connection (attempt {attempt}/{max_attempts})...")
            client = MongoClient(
                MONGO_URI,
                tls=True,
                tlsAllowInvalidCertificates=False,  # Set to True only for testing (not recommended)
                serverSelectionTimeoutMS=60000,
                connectTimeoutMS=60000,
                socketTimeoutMS=60000,
                retryWrites=True,
                w='majority'
            )
            # Test the connection
            client.admin.command('ping')
            logger.info("Successfully connected to MongoDB.")
            return client
        
        except (ConnectionFailure, AutoReconnect) as e:
            logger.error(f"MongoDB connection attempt {attempt} failed: {e}")
            if attempt == max_attempts:
                logger.error("Max connection attempts reached. Aborting.")
                raise
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            attempt += 1
            delay *= 2  # Exponential backoff
    return None

def process_batch(batch, pg_conn):
    try:
        pg_cursor = pg_conn.cursor()
        retrieved_on = datetime.now()

        # Prepare bulk insert data
        stores_data = []
        products_data = []
        products_update_data = []
        prices_data = []

        for item in batch:
            store_name = item.get("store")
            product_name = item.get("name")
            product_url = item.get("url")
            image_urls = item.get("images", [])
            price = float(item.get("price", 0)) if item.get("price") else 0.0
            is_active = item.get("is_active", True)

            if not all([store_name, product_name, product_url]) or not image_urls:
                logger.warning(f"Skipping record due to missing fields: {item}")
                continue

            # Filter out invalid image URLs
            valid_image_urls = [url for url in image_urls if url and url.strip() and url.startswith("https:") and url.endswith((".jpg", ".png", ".jpeg"))]
            if not valid_image_urls:
                logger.warning(f"Skipping record due to no valid image URLs: {item}")
                continue

            # Ensure the store exists
            pg_cursor.execute("SELECT store_id FROM stores WHERE store_name = %s", (store_name,))
            store_result = pg_cursor.fetchone()

            if store_result is None:
                stores_data.append((store_name, retrieved_on))
                pg_cursor.execute(
                    "INSERT INTO stores (store_name, last_retrieved_on) VALUES (%s, %s) RETURNING store_id",
                    (store_name, retrieved_on),
                )
                store_id = pg_cursor.fetchone()[0]
            else:
                store_id = store_result[0]

            # Check if the product exists
            pg_cursor.execute("SELECT product_id FROM products WHERE product_url = %s", (product_url,))
            product_result = pg_cursor.fetchone()

            if product_result is None:
                # Insert new product
                products_data.append((store_id, product_name, product_url, valid_image_urls, int(price), is_active))
                pg_cursor.execute(
                    """
                    INSERT INTO products (store_id, product_name, product_url, image_urls, latest_price, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id
                    """,
                    (store_id, product_name, product_url, valid_image_urls, int(price), is_active),
                )
                product_id = pg_cursor.fetchone()[0]
            else:
                # Update existing product
                product_id = product_result[0]
                products_update_data.append((product_id, product_name, valid_image_urls, int(price), is_active))

            # Insert price history
            prices_data.append((product_id, int(price), retrieved_on))

        # Bulk insert stores
        if stores_data:
            execute_batch(pg_cursor, "INSERT INTO stores (store_name, last_retrieved_on) VALUES (%s, %s)", stores_data)

        # Bulk insert new products
        if products_data:
            execute_batch(
                pg_cursor,
                """
                INSERT INTO products (store_id, product_name, product_url, image_urls, latest_price, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                products_data,
            )

        # Bulk update existing products
        if products_update_data:
            execute_batch(
                pg_cursor,
                """
                UPDATE products
                SET product_name = %s, image_urls = %s, latest_price = %s, is_active = %s
                WHERE product_id = %s
                """,
                [(name, urls, price, active, pid) for (pid, name, urls, price, active) in products_update_data],
            )

        # Bulk insert price history
        if prices_data:
            execute_batch(
                pg_cursor,
                "INSERT INTO product_prices (product_id, price, retrieved_on) VALUES (%s, %s, %s)",
                prices_data,
            )

        pg_conn.commit()
        logger.info(f"Processed batch of {len(batch)} records.")

    except Exception as e:
        logger.error(f"Failed to process batch: {e}")
        pg_conn.rollback()
    finally:
        pg_cursor.close()

def main():
    try:
        # Connect to MongoDB with retry
        mongo_client = connect_mongo_with_retry()
        if not mongo_client:
            logger.error("Failed to connect to MongoDB after retries.")
            return

        mongo_db = mongo_client[MONGO_DB]
        mongo_collection = mongo_db[MONGO_COLLECTION]

        # Connect to PostgreSQL
        pg_conn = psycopg2.connect(POSTGRES_URI)
        logger.info("Connected to PostgreSQL.")

        # Fetch data from MongoDB
        logger.info("Fetching data from MongoDB...")
        mongo_data = list(mongo_collection.find({}))
        logger.info(f"Retrieved {len(mongo_data)} records from MongoDB.")
        batch_size = 100  # Process in batches of 100
        batches = [mongo_data[i:i + batch_size] for i in range(0, len(mongo_data), batch_size)]

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            for batch in batches:
                executor.submit(process_batch, batch, pg_conn)

        logger.info("Migration completed successfully.")

    except Exception as e:
        logger.error(f"Migration failed: {e}")

    finally:
        # Close connections
        if 'pg_conn' in locals():
            pg_conn.close()
        if 'mongo_client' in locals():
            mongo_client.close()
        logger.info("Database connections closed.")

if __name__ == "__main__":
    main()