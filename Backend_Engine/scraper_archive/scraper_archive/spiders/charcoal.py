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
            price_str = price_str.replace('Rs.', '').replace(',', '').strip()
            return float(price_str)
        except ValueError:
            return 0.0

    def parse(self, response):
        products = response.css("product-card")

        for product in products:
            # Extract product URL
            url_path = product.css("a::attr(href)").get()
            product_url = urljoin(response.url, url_path)

            # Extract product title
            title = product.css("span.product-card__title a::text").get()
            if title:
                title = title.strip()

            sale_price = product.xpath(".//sale-price/text()[normalize-space()]").get()
            original_price = product.xpath(".//compare-at-price/text()[normalize-space()]").get()

            #print("MAH DICK",sale_price, original_price)

            price = self.clean_price(sale_price) if sale_price else self.clean_price(original_price)

            # Extract image
            image_urls = product.css("img.product-card__image--primary::attr(srcset)").get()
            images = []

            for img in product.css("img.product-card__image::attr(srcset)").getall():
                try:
                    high_res = img.split(",")[-1].split(" ")[0].strip()
                    if high_res.startswith("//"):
                        high_res = "https:" + high_res
                    images.append(high_res)
                except Exception:
                    continue

            # Detect if it's on sale or out of stock (rough logic — adjust based on real indicators)
            is_active = True  # No clear out-of-stock marker in provided HTML

            yield {
                'name': title,
                'price': price,
                'is_active': is_active,
                'images': list(set(images)),
                'url': product_url,
                'store': 'Charcoal',
            }

        # Handle pagination (Load More button or numbered pagination)
        next_page = response.css('a[href*="/collections/all?page="]::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)
