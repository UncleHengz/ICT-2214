import scrapy
import logging

# Disable all logging
logging.disable(logging.CRITICAL)

class SSLSpider(scrapy.Spider):
    name = 'ssl_spider'

    def start_requests(self):
        # Get the URL from the command-line argument
        url = getattr(self, 'url', None)
        if url is not None:
            # Use the URL directly in the request
            yield scrapy.Request(url, self.parse)
        else:
            print('URL not provided. Use the -a option to specify the URL. Example: scrapy crawl ssl_spider -a url=https://www.example.com')

    def parse(self, response):
        # Check if the response URL starts with 'https://'
        if response.url.startswith('https://'):
            print(f"{response.url} is SSL certified.")
        else:
            print(f"{response.url} is not SSL certified.")