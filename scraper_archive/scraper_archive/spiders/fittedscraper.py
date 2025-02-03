import scrapy
from urllib.parse import urljoin

class FittedShopSpider(scrapy.Spider):
    name = "fittedshop"
    allowed_domains = ["fittedshop.com"]
    start_urls = ["https://fittedshop.com/collections/all"]

    def is_male_product(self, title):
        """Determine if the product is for males"""
        female_keywords = ['(WOMEN)', "women's", "womens"]
        return not any(keyword.lower() in title.lower() for keyword in female_keywords)

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
        """Parse the collection page and navigate through pagination"""
        products = response.css('a.grid-product__link')
        for product in products:
            title = product.css('div.grid-product__title::text').get()
            if title:
                title = title.strip()

            # Extract price elements
            sale_price_elem = product.css('span.grid-product__price--original::text').get()
            original_price_elem = product.css('div.grid-product__price::text').get()
            
            # Use sale price if available, otherwise use original price
            price = self.clean_price(sale_price_elem) if sale_price_elem else self.clean_price(original_price_elem)

            product_url = urljoin(response.url, product.attrib['href'])

            if self.is_male_product(title):
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
            'store': 'Fitted Shop',
        }
