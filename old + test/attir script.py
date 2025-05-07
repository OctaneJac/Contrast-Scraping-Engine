import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(POSTGRES_URI)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    print("✅ PostgreSQL connection successful")
except Exception as e:
    print("❌ PostgreSQL connection failed:", e)
    exit()

# Step 1: Query products from 'Attir Store'
try:
    cursor.execute("SELECT * FROM products WHERE store_id = '5'")
    products = cursor.fetchall()
except Exception as e:
    print("❌ Failed to query products:", e)
    conn.close()
    exit()

# Step 2: Scrape and update latest_price
for product in products:
    product_url = product.get("product_url")
    product_id = product.get("product_id")

    try:
        response = requests.get(product_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try sale price first
        price_tag = soup.find(class_="price-item price-item--sale price-item--last")
        if not price_tag:
            # Try regular price if sale price not found
            price_tag = soup.find(class_="price-item price-item--regular")

        if price_tag:
            # Clean and parse price
            price_text = price_tag.get_text(strip=True)
            print(price_text)
            price_text = price_text.replace("Rs", "").replace(" ", "").replace(",", "").replace(".", "", 1)
            print(price_text)
            try:
                price = float(price_text)
            except ValueError:
                print(f"⚠️ Unable to parse price: {price_text}")
                continue

            # Update in PostgreSQL
            update_query = "UPDATE products SET latest_price = %s WHERE product_id = %s"
            cursor.execute(update_query, (price, product_id))
            conn.commit()

            print(f"✅ Updated product {product_id} with price {price}")
        else:
            print(f"⚠️ Price not found for {product_url}")

    except Exception as e:
        print(f"❌ Failed to scrape {product_url}: {e}")

# Cleanup
cursor.close()
conn.close()
