import scrapy
from urllib.parse import urljoin


class AttirStoreSpider(scrapy.Spider):
    name = 'Attir Store'
    allowed_domains = ['attirstore.com']
    start_urls = ['https://attirstore.com/collections/all']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36'
    }
    page = 1

    def clean_price(self, price_str):
        """Clean and convert price to float."""
        try:
            if not price_str:
                return 0.0
            price_str = price_str.replace("Rs", "").replace(" ", "").replace(",", "")
            price_float = float(price_str)
            # If the price is less than 1, assume it's in the wrong format (e.g., 0.1113) and scale it up
            if price_float < 1:
                price_float *= 10000
            return price_float
        except ValueError:
            self.logger.warning(f"⚠️ Could not convert price: {price_str}")
            return 0.0

    def parse(self, response):
        self.logger.info("🔍 Parsing collection page...")

        # ✅ Updated product selector to wrapper that includes prices
        products = response.css('.card-wrapper')

        for product in products:
            link = product.css('.card__heading a::attr(href)').get()
            title = product.css('.card__heading a::text').get()

            if not link:
                continue

            product_url = urljoin(response.url, link)
            title = title.strip() if title else 'Unknown'

            # ✅ Try sale price first, then regular
            price_text = product.css('.price-item--sale::text').get()
            if not price_text:
                price_text = product.css('.price-item--regular::text').get()

            price = self.clean_price(price_text.strip() if price_text else "")

            # ✅ Check for sold out
            sold_out_text = product.css('.card__badge span.badge::text').get()
            is_sold_out = sold_out_text and "Sold out" in sold_out_text
            is_active = not is_sold_out
            if is_sold_out:
                price = 0.0

            yield scrapy.Request(
                url=product_url,
                callback=self.parse_product,
                headers=self.custom_settings,
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
        else:
            self.page += 1
            next_url = f'https://attirstore.com/collections/all?page={self.page}'
            if products:
                self.logger.info(f"⏭️ Trying next manual page: {next_url}")
                yield scrapy.Request(next_url, callback=self.parse)
            else:
                self.logger.info("✅ No more products found, stopping.")

    def parse_product(self, response):
        """Parse individual product page to extract images."""
        title = response.meta['title']
        price = response.meta['price']
        product_url = response.meta['url']
        is_active = response.meta['is_active']

        image_srcsets = response.css('product-modal img::attr(srcset)').getall()
        if not image_srcsets:
            image_srcsets = response.css('.product__media img::attr(srcset)').getall()

        images = []
        for srcset in image_srcsets:
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
            'store': 'Attir Store',
            'is_active': is_active
        }
