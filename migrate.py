
import os
import psycopg2
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Ensure all environment variables are loaded
if not all([MONGO_URI, MONGO_DB, MONGO_COLLECTION, POSTGRES_URI]):
    print("[ERROR] One or more environment variables are missing.")
    exit(1)

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

finally:
    # Close connections
    if 'pg_cursor' in locals():
        pg_cursor.close()
    if 'pg_conn' in locals():
        pg_conn.close()
    if 'mongo_client' in locals():
        mongo_client.close()
    print("[INFO] Database connections closed.")
