import scrapy
from urllib.parse import urljoin

class AvantGardeSpider(scrapy.Spider):
    name = "avantgarde"
    allowed_domains = ["avantgardeoriginal.com"]
    start_urls = ["https://avantgardeoriginal.com/collections/all"]

    def clean_price(self, price_str):
        """Clean and convert price to float"""
        try:
            if not price_str:
                return 0.0
            price_str = price_str.replace('$', '').replace(',', '').strip()
            return float(price_str)
        except ValueError:
            return 0.0

    def parse(self, response):
        """Parse the collection page and navigate through pagination"""
        products = response.css('div.card__content')
        for product in products:
            title_elem = product.css('h3.card__heading a::text')
            title = title_elem.get().strip() if title_elem else None

            product_url_elem = product.css('h3.card__heading a::attr(href)')
            product_url = urljoin(response.url, product_url_elem.get()) if product_url_elem else None

            sale_price_elem = product.css('span.price--sale::text').get()
            original_price_elem = product.css('span.price-item--regular::text').get()

            # If product is marked as Sold Out, set price to 0
            sold_out = product.css('div.card__badge span.badge::text').get()
            if sold_out and "Sold out" in sold_out:
                price = 0.0
            else:
                # Use sale price if available, otherwise use original price
                price = self.clean_price(sale_price_elem) if sale_price_elem else self.clean_price(original_price_elem)

            if product_url:
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
        """Parse individual product pages"""
        title = response.meta['title']
        price = response.meta['price']
        product_url = response.meta['url']

        # Extract image URL
        image_url = response.css('img::attr(srcset)').get()
        if image_url:
            # Get the highest resolution image by splitting srcset and taking the last one
            image_url = image_url.split(",")[-1].split(" ")[0]

        # Ensure the image URL is complete
        if image_url and image_url.startswith("//"):
            image_url = "https:" + image_url

        # Yield product data
        yield {
            'name': title,
            'price': price,
            'image': image_url,
            'url': product_url,
            'store': 'Avant Garde',
        }
