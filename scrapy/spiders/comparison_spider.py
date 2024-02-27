import scrapy
from project_name.items import WebContentItem

class ComparisonSpider(scrapy.Spider):
    name = 'comparison'
    start_urls = [
        'https://www.singaporetech.edu.sg/',
    ]

    def parse(self, response):
        item = WebContentItem()
        item['url'] = response.url
        item['content'] = response.text
        yield item