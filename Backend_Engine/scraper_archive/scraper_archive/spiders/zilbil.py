import scrapy
from urllib.parse import urljoin

class ZilbilSpider(scrapy.Spider):
    name = "zilbil"
    allowed_domains = ["zilbil.store"]
    start_urls = ["https://zilbil.store/collections/all"]

    def clean_price(self, price_str):
        """Convert price text to float, removing extra characters."""
        try:
            if not price_str:
                return 0.0
            price_str = price_str.replace('Rs.', '').replace(',', '').strip()
            return float(price_str)
        except ValueError:
            return 0.0

    def parse(self, response):
        """Parse the collection page and navigate through pagination."""
        products = response.css('div.product-item')
        print("classes might be wrong but scraper itself is working")

        for product in products:
            product_link = product.css('a.product-item__image-link')
            title = product_link.attrib.get('aria-label', '').strip() if product_link else ''

            # Skip products that contain "pack" in the title
            if "pack" in title.lower():
                continue

            product_url = urljoin(response.url, product_link.attrib['href']) if product_link else None
            if not product_url:
                continue

            # Extract price details
            sale_price_elem = product.css('span.price--sale::text').get()
            original_price_elem = product.css('span.price--regular::text').get()

            # Extract sold-out badge
            sold_out = product.css('span.badge--sold-out::text').get()

            # If sold out, set price to 0; otherwise, get the correct price
            price = 0.0 if sold_out else self.clean_price(sale_price_elem) if sale_price_elem else self.clean_price(original_price_elem)

            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta={'title': title, 'price': price, 'url': product_url},
            )

        # Follow pagination
        next_page = response.css('a.pagination__next::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_product(self, response):
        """Parse individual product pages."""
        title = response.meta.get('title', 'Unknown Product')
        price = response.meta.get('price', 0.0)
        product_url = response.meta.get('url', response.url)

        # Extract image URL(s)
        image_urls = response.css('img.image__img::attr(src)').getall()
        primary_image = urljoin(response.url, image_urls[0]) if image_urls else None

        yield {
            'name': title,
            'price': price,
            'image': primary_image,
            'url': product_url,
            'store': 'Zilbil',
        }
