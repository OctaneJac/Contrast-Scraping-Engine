import scrapy
from urllib.parse import urljoin

class avantgarde(scrapy.Spider):
    name = "avantgarde"
    allowed_domains = ["avantgardeoriginal.com"]
    start_urls = ["https://avantgardeoriginal.com/collections/all"]

    def clean_price(self, price_str):
        """Clean and convert price to float"""
        try:
            if not price_str:
                return 0.0
            price_str = price_str.replace('Rs.', '').replace(',', '').strip()
            return float(price_str)
        except ValueError:
            return 0.0

    def parse(self, response):
        """Parse the collection page and extract product links"""
        products = response.css('div.card-wrapper.product-card-wrapper')

        for product in products:
            link_elem = product.css('a.full-unstyled-link::attr(href)').get()
            title_elem = product.css('a.full-unstyled-link::text').get()

            if not link_elem:
                continue

            title = title_elem.strip() if title_elem else None
            product_url = urljoin(response.url, link_elem)

            # Price & Sold Out
            sale_price = product.css('span.price-item--sale .money::text').get()
            regular_price = product.css('span.price-item--regular .money::text').get()

            sold_out = product.css('div.card__badge span.badge::text').get()
            is_sold_out = sold_out and "Sold out" in sold_out

            price = 0.0 if is_sold_out else self.clean_price(sale_price or regular_price)
            is_active = not is_sold_out

            yield scrapy.Request(
                url=product_url,
                callback=self.parse_product,
                meta={
                    'title': title,
                    'price': price,
                    'url': product_url,
                    'is_active': is_active
                }
            )

        # Pagination
        next_page = response.css('a.pagination__next::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_product(self, response):
        """Parse individual product page and collect all image URLs"""
        title = response.meta['title']
        price = response.meta['price']
        product_url = response.meta['url']
        is_active = response.meta['is_active']

        image_urls = response.css('product-modal img::attr(srcset)').getall()

        images = []
        for srcset in image_urls:
            try:
                high_res = srcset.split(",")[-1].split(" ")[0].strip()
                if high_res.startswith("//"):
                    high_res = "https:" + high_res
                images.append(high_res)
            except IndexError:
                continue

        images = list(set(images))

        yield {
            'name': title,
            'price': price,
            'images': images,
            'url': product_url,
            'store': 'Avant Garde',
            'is_active': is_active
        }
