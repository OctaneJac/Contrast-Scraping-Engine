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
        products = response.css('div.product-item__inner')

        for product in products:
            product_link = product.css('a.product-item__image-link')
            title = product_link.attrib.get('aria-label', '').strip() if product_link else ''

            if "pack" in title.lower():
                continue

            product_url = urljoin(response.url, product_link.attrib['href']) if product_link else None
            if not product_url:
                continue

            sale_price = product.css('span.sale::text').get()
            regular_price = product.css('s.t-subdued::text').get()
            sold_out = product.css('.product-badge--sold-out::text').get()

            price = self.clean_price(sale_price or regular_price)
            is_active = False if sold_out else True

            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta={'title': title, 'price': price, 'url': product_url, 'is_active': is_active},
            )

        # Fix: Identify next page from pagination
        current_page = response.css('span.pagination__item--current::text').get()
        if current_page:
            try:
                next_page_number = int(current_page) + 1
                next_page_url = f"https://zilbil.store/collections/all?page={next_page_number}"
                yield scrapy.Request(next_page_url, callback=self.parse)
            except ValueError:
                pass  # Skip if the current page is not an integer

    def parse_product(self, response):
        """Parse individual product pages."""
        title = response.meta.get('title', 'Unknown Product')
        price = response.meta.get('price', 0.0)
        product_url = response.meta.get('url', response.url)
        is_active = response.meta.get('is_active', True)

        # Extract image URL(s)
        image_urls = response.css('img.image__img::attr(src)').getall()
        image_urls = [urljoin(response.url, url) for url in image_urls if url]

        yield {
            'name': title,
            'price': price,
            'images': image_urls[:4],
            'url': product_url,
            'store': 'Zilbil',
            'is_active': is_active,
        }
