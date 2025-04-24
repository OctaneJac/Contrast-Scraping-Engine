import scrapy
from urllib.parse import urljoin

class fittedshop(scrapy.Spider):
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

            # Determine sold-out status
            sold_out = product.css('span.grid-product__badge::text').get()
            is_active = False if sold_out and "Sold Out" in sold_out else True

            product_url = urljoin(response.url, product.attrib['href'])

            if self.is_male_product(title):
                yield scrapy.Request(
                    product_url,
                    callback=self.parse_product,
                    meta={
                        'title': title,
                        'price': price,
                        'url': product_url,
                        'is_active': is_active
                    },
                )

        # Follow pagination
        next_page = response.css('a.pagination__next::attr(href)').get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_product(self, response):
        """Parse individual product pages and extract all images"""
        title = response.meta['title']
        price = response.meta['price']
        product_url = response.meta['url']
        is_active = response.meta['is_active']

        images = []

        # Extract main product images from image-element tags using data-photoswipe-src
        main_images = response.css('image-element img::attr(data-photoswipe-src)').getall()
        for img in main_images:
            if img.startswith("//"):
                img = "https:" + img
            images.append(img)

        # Extract thumbnail images from product__thumbs section using srcset
        thumb_images = response.css('div.product__thumbs image-element img::attr(srcset)').getall()
        for srcset in thumb_images:
            try:
                # Get the highest resolution from srcset
                high_res = srcset.split(",")[-1].split(" ")[0].strip()
                if high_res.startswith("//"):
                    high_res = "https:" + high_res
                images.append(high_res)
            except IndexError:
                continue

        # Remove duplicates and ensure unique images
        images = list(set(images))
        for i in images:
            if i == "":
                images.remove(i)

        yield {
            'name': title,
            'price': price,
            'is_active': is_active,
            'images': images,
            'url': product_url,
            'store': 'Fitted Shop',
        }