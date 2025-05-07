import os
from dotenv import load_dotenv
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from pymongo.errors import ServerSelectionTimeoutError
from itertools import islice

# Load environment variables
load_dotenv()
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
POSTGRES_URI = os.getenv("POSTGRES_URI")

# MongoDB connection
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

# Connect to PostgreSQL
pg_conn = psycopg2.connect(POSTGRES_URI)
pg_cursor = pg_conn.cursor()

def get_or_insert_stores(store_names, pg_cursor, pg_conn):
    """Bulk fetch or insert stores, return a dictionary of store_name -> store_id."""
    now = datetime.utcnow()
    store_id_map = {}

    # Fetch existing stores
    placeholders = ','.join(['%s'] * len(store_names))
    pg_cursor.execute(f"SELECT store_name, store_id FROM stores WHERE store_name IN ({placeholders})", tuple(store_names))
    for store_name, store_id in pg_cursor.fetchall():
        store_id_map[store_name] = store_id
        # Update last_retrieved_on
        pg_cursor.execute(
            "UPDATE stores SET last_retrieved_on = %s WHERE store_id = %s",
            (now, store_id)
        )

    # Insert new stores
    new_stores = [(name, now, now) for name in store_names if name not in store_id_map]
    if new_stores:
        execute_values(
            pg_cursor,
            "INSERT INTO stores (store_name, last_retrieved_on, created_at) VALUES %s RETURNING store_name, store_id",
            new_stores,
            template="(%s, %s, %s)"
        )
        for store_name, store_id in pg_cursor.fetchall():
            store_id_map[store_name] = store_id

    pg_conn.commit()
    return store_id_map

def process_batch(products, pg_cursor, pg_conn):
    """Process a batch of products with bulk inserts/upserts."""
    if not products:
        return

    now = datetime.utcnow()
    
    # Cache store IDs
    store_names = list(set(doc.get("store") for doc in products))
    store_id_map = get_or_insert_stores(store_names, pg_cursor, pg_conn)

    # Prepare product data
    product_data = []
    price_history_data = []
    for doc in products:
        store_name = doc.get("store")
        store_id = store_id_map.get(store_name)
        if not store_id:
            print(f"Skipping product with invalid store: {doc.get('name')}")
            continue

        product_url = doc.get("url")
        product_name = doc.get("name")
        is_active = doc.get("is_active", True)
        price_str = doc.get("price", "0")
        
        # Handle non-numeric prices
        try:
            price = int(float(price_str))
        except (ValueError, TypeError):
            print(f"Invalid price '{price_str}' for product: {product_name}. Using default price 0.")
            continue  # Or skip: continue

        images = doc.get("images", [])
        image_urls = images if isinstance(images, list) else []

        product_data.append((store_id, is_active, now, price, image_urls, '', product_name, product_url))
        price_history_data.append((product_url, price, now))

    if not product_data:
        return

    # Bulk check existing products
    product_urls = [p[7] for p in product_data]  # product_url is 8th column
    placeholders = ','.join(['%s'] * len(product_urls))
    pg_cursor.execute(f"SELECT product_url, product_id FROM products WHERE product_url IN ({placeholders})", tuple(product_urls))
    existing_products = {row[0]: row[1] for row in pg_cursor.fetchall()}

    # Separate new and existing products
    new_products = [p for p in product_data if p[7] not in existing_products]
    update_products = []
    for p in product_data:
        if p[7] in existing_products:
            product_id = existing_products[p[7]]
            update_products.append((p[1], p[3], p[4], p[6], product_id))  # is_active, latest_price, image_urls, product_name, product_id

    # Bulk insert new products
    if new_products:
        execute_values(
            pg_cursor,
            """
            INSERT INTO products 
            (store_id, is_active, created_at, latest_price, image_urls, categories, product_name, product_url)
            VALUES %s
            RETURNING product_id, product_url
            """,
            new_products,
            template="(%s, %s, %s, %s, %s, %s, %s, %s)"
        )
        # Update existing_products with new product_ids
        for product_id, product_url in pg_cursor.fetchall():
            existing_products[product_url] = product_id

    # Bulk update existing products
    if update_products:
        execute_values(
            pg_cursor,
            """
            UPDATE products SET
                is_active = data.is_active,
                latest_price = data.latest_price,
                image_urls = data.image_urls,
                product_name = data.product_name
            FROM (VALUES %s) AS data (is_active, latest_price, image_urls, product_name, product_id)
            WHERE products.product_id = data.product_id
            """,
            update_products,
            template="(%s, %s, %s, %s, %s)"
        )

    # Bulk insert price history
    price_history_with_ids = [(existing_products[p[0]], p[1], p[2]) for p in price_history_data if p[0] in existing_products]
    if price_history_with_ids:
        execute_values(
            pg_cursor,
            "INSERT INTO product_prices (product_id, price, retrieved_on) VALUES %s",
            price_history_with_ids,
            template="(%s, %s, %s)"
        )

    pg_conn.commit()
    print(f"✅ Processed batch of {len(product_data)} products")

def main():
    # Fetch products with batching
    BATCH_SIZE = 1000
    products = mongo_collection.find().batch_size(BATCH_SIZE)
    total_processed = 0

    while True:
        batch = list(islice(products, BATCH_SIZE))
        if not batch:
            break
        process_batch(batch, pg_cursor, pg_conn)
        total_processed += len(batch)
        print(f"Total products processed: {total_processed}")

    print(f"✅ Migration complete. Total products processed: {total_processed}")

# Cleanup
try:
    main()
finally:
    pg_cursor.close()
    pg_conn.close()
    mongo_client.close()