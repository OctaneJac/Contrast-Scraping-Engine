import scrapy
from urllib.parse import urljoin

class LamaretailSpider(scrapy.Spider):
    name = "Lama Retail"
    allowed_domains = ["lamaretail.com"]
    start_urls = ["https://lamaretail.com/collections/all"]

    def clean_price(self, price_str):
        """Convert price string like 'Rs.9,450.00' to float."""
        try:
            return float(price_str.replace("Rs.", "").replace(",", "").strip())
        except (ValueError, AttributeError):
            return 0.0

    def parse(self, response):
        products = response.css("div.grid-product")

        for product in products:
            base_url = response.url

            # Extract base title
            base_title = product.css(".grid-product__title::text").get()
            if not base_title:
                continue
            base_title = base_title.strip()

            # Extract sale price first, then fallback to original price
            sale_price = product.css(".grid-product__price--sale .money::text").get()
            original_price = product.css(".grid-product__price .money::text").get()
            price = self.clean_price(sale_price) if sale_price else self.clean_price(original_price)

            # Extract image URLs
            img_tags = product.css("img::attr(src)").getall()
            images = []
            for img in img_tags:
                full_url = urljoin(base_url, img)
                if full_url not in images:
                    images.append(full_url)

            # Extract product page URL to check stock status later
            product_relative_url = product.css("a.grid-product__link::attr(href)").get()
            product_url = urljoin(base_url, product_relative_url) if product_relative_url else base_url

            # Follow the product link to check its stock status
            yield scrapy.Request(
                product_url,
                callback=self.parse_product,
                meta={
                    'title': base_title,
                    'price': price,
                    'images': images[:4],
                    'url': product_url
                }
            )

        # Handle pagination
        next_page = response.css("a.pagination__next::attr(href)").get()
        if next_page:
            yield scrapy.Request(urljoin(response.url, next_page), callback=self.parse)

    def parse_product(self, response):
        """Parse individual product page."""
        title = response.meta['title']
        price = response.meta['price']
        images = response.meta['images']
        product_url = response.meta['url']

        # Check for stock status by inspecting the "Add to Cart" button
        add_to_cart_button = response.css('button[data-add-to-cart]')
        is_active = True
        if add_to_cart_button and "disabled" in add_to_cart_button.attrib.get('class', ''):
            print("HELL YEA")
            is_active = False

        # Extract color variants if they exist
        color_links = response.css(".swatch-view-item a")
        if color_links:
            for color_link in color_links:
                color_name = color_link.css("span.visually-hidden::text").get(default="").strip()
                variant_url = color_link.attrib.get("href", "").strip()
                full_variant_url = urljoin(response.url, variant_url)

                yield {
                    'name': f"{color_name.upper()} {title}",
                    'price': price,
                    'images': images[:4],
                    'url': full_variant_url,
                    'store': 'Lama Retail',
                    'is_active': is_active
                }
        else:
            # No color variants; yield the single product
            yield {
                'name': title,
                'price': price,
                'images': images[:4],
                'url': product_url,
                'store': 'Lama Retail',
                'is_active': is_active
            }
