import scrapy
from scrapy.http import Request
from urllib.parse import urljoin, urlencode

class OutfittersSpider(scrapy.Spider):
    name = 'Outfitters'
    start_urls = ['https://outfitters.com.pk/collections/all']
    
    # Add headers to mimic a browser
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
    }

    def start_requests(self):
        # Initialize page counter
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={'page': 1})

    def parse(self, response):
        page = response.meta.get('page', 1)
        
        # Stop crawling after page 30
        if page > 30:
            self.logger.info(f'Reached page limit of 30. Stopping pagination.')
            return

        self.logger.info(f'Scraping page {page}: {response.url}')
        
        # Extract product cards
        product_cards = response.css('div.card__information')
        self.logger.info(f'Found {len(product_cards)} product cards on page {page}')

        if not product_cards:
            self.logger.warning(f'No product cards found on page {page}, stopping pagination')
            return

        for card in product_cards:
            # Extract product name
            title = card.css('h3.card__heading a::text').get(default='').strip()
            if not title:
                self.logger.warning('Skipping product with no title')
                continue

            # Extract product URL
            relative_url = card.css('h3.card__heading a::attr(href)').get(default='')
            product_url = urljoin(response.url, relative_url)

            # Extract price (sale price if available, else regular price)
            sale_price = card.css('span.price-item--sale .money::text').get(default='').strip()
            regular_price = card.css('span.price-item--regular .money::text').get(default='').strip()
            price = sale_price if sale_price else regular_price
            price = price.replace('PKR', '').replace(',', '').strip() if price else 'N/A'

            # Handle color variants (or default to no color if none exist)
            swatches = card.css('div.cstm-color-variants div.item-label div.item-image-wrapper')
            self.logger.info(f'Found {len(swatches)} color variants for product: {title}')
            
            if not swatches:
                # Handle products without color variants
                colored_title = title
                images = card.css('div[data-alt]::attr(data-image)').getall()[:4]  # Fallback to any images
                images = [img.strip() for img in images if img.strip()]
                images = list(dict.fromkeys(images))[:4]  # Remove duplicates
                
                is_active = True
                out_of_stock_badge = card.css('span.badge:contains("Sold Out")').get()
                if out_of_stock_badge:
                    is_active = False

                yield {
                    'name': colored_title,
                    'price': price,
                    'images': images,
                    'url': product_url,
                    'store': 'Outfitters',
                    'is_active': is_active
                }
                continue

            # Process each color variant
            for swatch in swatches:
                color = swatch.css('::attr(data-value)').get(default='').strip()
                color = color.replace('\n', '').strip() if color else 'Unknown'

                # Handle product name based on color
                if color.lower() == 'multi-colour':
                    colored_title = title  # Use original title without color
                else:
                    colored_title = f"{color.capitalize()} {title}"

                # Extract image URLs for this color variant
                image_elements = card.css(f'div[data-alt="{color}"]::attr(data-image)').getall()
                images = [img.strip() for img in image_elements if img.strip()]
                images = list(dict.fromkeys(images))[:4]  # Remove duplicates and limit to 4 images

                # Check if product is out of stock
                is_active = True
                out_of_stock_badge = card.css('span.badge:contains("Sold Out")').get()
                if out_of_stock_badge:
                    is_active = False

                # Yield the product data
                yield {
                    'name': colored_title,
                    'price': price,
                    'images': images,
                    'url': product_url,
                    'store': 'Outfitters',
                    'is_active': is_active
                }

        # Generate the next page URL
        next_page = page + 1
        next_page_url = f'https://outfitters.com.pk/collections/all?{urlencode({"page": next_page})}'
        self.logger.info(f'Requesting next page {next_page}: {next_page_url}')
        yield Request(next_page_url, callback=self.parse, meta={'page': next_page})