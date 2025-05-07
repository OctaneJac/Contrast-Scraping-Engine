import os
from dotenv import load_dotenv
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
from datetime import datetime
from pymongo.errors import ServerSelectionTimeoutError
from concurrent.futures import ThreadPoolExecutor

# Load env variables
load_dotenv()
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
POSTGRES_URI = os.getenv("POSTGRES_URI")

uri = "mongodb+srv://uzairrafiq2002:LNTUPilQmnn48mkM@contrast-cluster.ntwdscu.mongodb.net/?retryWrites=true&w=majority"

try:
    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=15000,
        tls=True,
        tlsAllowInvalidCertificates=False,
    )
    db = client["Contrast"]
    print("✅ MongoDB connection successful")

except ServerSelectionTimeoutError as e:
    print("❌ MongoDB connection failed:", e)

# Validate env vars
if not all([MONGO_DB, MONGO_COLLECTION, POSTGRES_URI]):
    raise Exception("Missing one or more required environment variables.")

# Connect to MongoDB
mongo_client = MongoClient(uri)
mongo_collection = mongo_client[MONGO_DB][MONGO_COLLECTION]

# PostgreSQL connection pool
pg_pool = ThreadedConnectionPool(1, 10, POSTGRES_URI)

def get_or_insert_store(store_name, pg_conn):
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT store_id FROM stores WHERE store_name = %s", (store_name,))
    result = pg_cursor.fetchone()
    now = datetime.utcnow()
    if result:
        store_id = result[0]
        # Update existing store's last_retrieved_on and updated_at fields
        pg_cursor.execute(
            "UPDATE stores SET last_retrieved_on = %s WHERE store_id = %s",
            (now, store_id)
        )
        pg_conn.commit()
        return store_id
    # Insert new store if not exists
    pg_cursor.execute(
        "INSERT INTO stores ( store_name, last_retrieved_on, created_at) VALUES ( %s, %s, %s) RETURNING store_id",
        (store_name, now, now,)
    )
    store_id = pg_cursor.fetchone()[0]
    pg_conn.commit()
    return store_id

def process_document(doc):
    pg_conn = pg_pool.getconn()
    try:
        pg_cursor = pg_conn.cursor()

        store_name = doc.get("store")
        store_id = get_or_insert_store(store_name, pg_conn)

        product_url = doc.get("url")
        product_name = doc.get("name")
        is_active = doc.get("is_active", True)
        price = int(float(doc.get("price", 0)))
        images = doc.get("images", [])
        image_urls = images if isinstance(images, list) else []
        created_at = datetime.utcnow()

        # Check if product exists by URL
        pg_cursor.execute("SELECT product_id FROM products WHERE product_url = %s", (product_url,))
        existing = pg_cursor.fetchone()

        if existing:
            product_id = existing[0]
            # Update existing product
            pg_cursor.execute("""
                UPDATE products SET
                    is_active = %s,
                    latest_price = %s,
                    image_urls = %s,
                    product_name = %s
                WHERE product_id = %s
            """, (is_active, price, image_urls, product_name, product_id))
        else:
            # Insert new product
            pg_cursor.execute("""
                INSERT INTO products 
                (store_id, is_active, created_at, latest_price, image_urls, categories, product_name, product_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING product_id
            """, (store_id, is_active, created_at, price, image_urls, '', product_name, product_url))
            product_id = pg_cursor.fetchone()[0]

        # Add price history
        pg_cursor.execute("""
            INSERT INTO product_prices (product_id, price, retrieved_on)
            VALUES (%s, %s, %s)
        """, (product_id, price, created_at))

        pg_conn.commit()
    except Exception as e:
        print(f"❌ Error processing document: {e} for document {doc}")
    finally:
        pg_pool.putconn(pg_conn)

# Fetch products from MongoDB
mongo_products = mongo_collection.find()

# Use ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(process_document, mongo_products)
    print("✅ Products synced with price history updated.")


# Cleanup
pg_pool.closeall()
mongo_client.close()
