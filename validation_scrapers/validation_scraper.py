import asyncio
import aiohttp
import asyncpg
import os
import psycopg2
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re

load_dotenv()
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Each store has multiple price selectors to try in order
STORE_PRICE_SELECTORS = {
    "Fitted Shop": [".product__price"],
    "Outfitters": ["span.money", ".sale-price"],
    "store_3": [".price-container", ".discount-price", ".actual-price"],
    # Add multiple selectors for all 20 stores
}

# failed_urls = []
# failed_urls_lock = asyncio.Lock()

# async def retry_failed_urls():
#     async with aiohttp.ClientSession() as session:
#         for product_id, url in failed_urls:
#             print(f"🔄 Retrying {url}...")
#             price = await fetch(session, product_id, url, STORE_PRICE_SELECTORS["outfitters"])
#             if price[1] is not None:  # Only retry if price was fetched successfully
#                 await update_database([price])
#             else:
#                 print(f"🚨 Still failed: {url}")

async def fetch(session, product_id, url, price_selectors, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=20) as response:
                if response.status == 404:
                    return product_id, None, False  
                elif response.status != 200:
                    return product_id, None, True  

                html = await response.text()
                price = extract_price(html, price_selectors)

                return product_id, price, True
        
        except asyncio.TimeoutError:
            print(f"⏳ Timeout {attempt+1}/{retries} for {url}")
        except aiohttp.ClientError as e:
            print(f"🚨 Request failed {attempt+1}/{retries} for {url}: {str(e)}")

    # async with failed_urls_lock:  # Ensure only one coroutine writes at a time
    #     failed_urls.append((product_id, url))   
    return product_id, None, True  


def extract_price(html, price_selectors):
    """Extract price from HTML using multiple selectors"""
    soup = BeautifulSoup(html, "html.parser")

    for selector in price_selectors:
        price_tag = soup.select_one(selector)
        if price_tag:
            price_text = price_tag.text.strip()
            print(f"Raw price text found: {price_text}")

            # Extract full numeric price (handle thousands separators)
            match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?)", price_text)
            if match:
                cleaned_price = match.group(1).replace(",", "")  # Remove commas
                x = float(cleaned_price)
                print(f"Extracted price: {x}")
                return x  # Convert matched number to float
    
    print("⚠️ No price found in HTML!")
    return None  # Default return if no price is found

async def update_database(results):
    """Update product prices and status in PostgreSQL"""
    conn = psycopg2.connect(POSTGRES_URI)
    cur = conn.cursor()

    for product_id, price, is_active in results:
        print("✅ Price for product:", price, product_id)

        if not is_active:
            cur.execute("UPDATE products SET is_active = FALSE WHERE product_id = %s", (product_id,))
        elif price is not None:  # Ignore None prices
            cur.execute("SELECT latest_price FROM products WHERE product_id = %s", (product_id,))
            latest_price = cur.fetchone()

            if latest_price is None or latest_price[0] != price:
                cur.execute(
                    """
                    INSERT INTO product_prices (product_id, price, retrieved_on) 
                    VALUES (%s, %s, %s)
                    """,
                    (product_id, price, datetime.utcnow().replace(tzinfo=pytz.utc))
                )

                cur.execute(
                    "UPDATE products SET latest_price = %s WHERE product_id = %s",
                    (price, product_id)
                )
    
    conn.commit()
    cur.close()
    conn.close()

# import asyncpg

# async def update_database(results):
#     conn = await asyncpg.connect(POSTGRES_URI)

#     for product_id, price, is_active in results:
#         print("✅ Price for product:", price, product_id)

#         if not is_active:
#             await conn.execute("UPDATE products SET is_active = FALSE WHERE product_id = $1", product_id)
#         elif price is not None:
#             latest_price = await conn.fetchval("SELECT latest_price FROM products WHERE product_id = $1", product_id)

#             if latest_price is None or latest_price != price:
#                 await conn.execute(
#                     "INSERT INTO product_prices (product_id, price, retrieved_on) VALUES ($1, $2, $3)",
#                     product_id, price, datetime.utcnow().replace(tzinfo=pytz.utc)
#                 )
#                 await conn.execute("UPDATE products SET latest_price = $1 WHERE product_id = $2", price, product_id)
    
#     await conn.close()


async def run_store_validation(store_name):
    """Run validation scraper for a specific store"""
    if not isinstance(store_name, str):
        raise TypeError(f"Expected string for store_name, got {type(store_name)}: {store_name}")
    
    conn = psycopg2.connect(POSTGRES_URI)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT p.product_id, p.product_url 
        FROM products p
        JOIN stores s ON p.store_id = s.store_id
        WHERE TRIM(LOWER(s.store_name)) = TRIM(LOWER(%s))
        """,
        (store_name,)
    )
    
    products = cur.fetchall()
    cur.close()
    conn.close()

    price_selectors = STORE_PRICE_SELECTORS.get(store_name)
    if not price_selectors:
        print(f"Price selector missing for {store_name}")
        return

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, pid, url, price_selectors) for pid, url in products]
        results = await asyncio.gather(*tasks)

    await update_database(results)


#Validation Scraper Task (Runs every midnight, updates products)
# STORES = [
#     "Fitted Shop",
#     "Outfitters",
#     # Add all 20 stores here
# ]

# def validate_all_stores():
#     """Run validation scrapers for all stores in parallel"""
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(run_all_validations())

# async def run_all_validations():
#     """Run each store's scraper concurrently using asyncio"""
#     tasks = [run_store_validation(store_name) for store_name in STORES]
#     print("Async running validation scrapers...")
#     await asyncio.gather(*tasks)  # Runs all store scrapers in parallel
#     # await retry_failed_urls()


# validate_all_stores()
