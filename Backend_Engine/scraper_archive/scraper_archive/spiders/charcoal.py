import scrapy
from urllib.parse import urljoin

class CharcoalSpider(scrapy.Spider):
    name = "charcoal"
    allowed_domains = ["charcoal.com.pk"]
    start_urls = ["https://charcoal.com.pk/collections/all"]

    def clean_price(self, price_str):
        """Clean and convert price to float"""
        try:
            if not price_str:
                return 0.0
            price_str = price_str.replace('Rs.', '').replace(',', '').replace('PKR', '').strip()
            return float(price_str)
        except ValueError:
            return 0.0

    def parse(self, response):
        """Parse the collection page and handle pagination"""
        products = response.css('product-card a.product-card__image::attr(href)').getall()
        for product_href in products:
            product_url = urljoin(response.url, product_href)
            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta={
                    'url': product_url
                }
            )

        # Handle pagination via "Load More" button or next page link
        next_page = response.css('a[href*="/collections/all?page="]::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_product(self, response):
        """Parse individual product pages and extract all images"""
        product_url = response.meta['url']

        # Extract title
        title = response.css('h1.product__title::text').get()
        if title:
            title = title.strip()

        # Extract sale price first, fallback to original price
        sale_price = response.css('span.price--highlight::text').get()
        original_price = response.css('span.price--compare::text').get() or response.css('span.price::text').get()
        price = self.clean_price(sale_price) if sale_price else self.clean_price(original_price)

        # Determine sold-out status
        sold_out = response.css('span.sold-out::text').get()
        is_active = False if sold_out and "Sold Out" in sold_out.lower() else True

        # Extract all images from product gallery
        images = []
        gallery_images = response.css('div.product-gallery__media img::attr(srcset)').getall()
        for srcset in gallery_images:
            if not srcset or not srcset.strip():  # Skip empty or None srcset
                continue
            try:
                # Get the highest resolution from srcset (e.g., 2400w)
                high_res = srcset.split(",")[-1].split(" ")[0].strip()
                if high_res and high_res.strip():  # Check for non-empty
                    if high_res.startswith("//"):
                        high_res = "https:" + high_res
                    if high_res.startswith("https:") and high_res.endswith((".jpg", ".png", ".jpeg")):  # Validate URL
                        images.append(high_res)
            except (IndexError, AttributeError):
                continue

        # Remove duplicates and ensure unique images
        images = list(set(images))

        yield {
            'name': title,
            'price': price,
            'is_active': is_active,
            'images': images,
            'url': product_url,
            'store': 'Charcoal',
        }