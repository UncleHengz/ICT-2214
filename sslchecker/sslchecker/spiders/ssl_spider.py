import scrapy

class SSLSpider(scrapy.Spider):
    name = 'ssl_spider'
    start_urls = ['https://www.singaporetech.edu.sg/']  # List the URLs you want to check here

    def parse(self, response):
        # Check if the response URL starts with 'https://'
        if response.url.startswith('https://'):
            yield {
                'url': response.url,
                'ssl_certified': True
            }
        else:
            yield {
                'url': response.url,
                'ssl_certified': False
            }