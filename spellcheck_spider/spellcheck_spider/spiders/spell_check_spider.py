import scrapy
from spellchecker import SpellChecker

class SpellCheckSpider(scrapy.Spider):
    name = 'spell_check_spider'
    start_urls = ['https://www.singaporetech.edu.sg/']  # List the URLs you want to check here

    def parse(self, response):
        spell = SpellChecker()
        text = response.xpath('//body//text()').extract()
        text = ' '.join(text)
        words = text.split()
        misspelled = spell.unknown(words)

        status = "Scam website" if len(misspelled) > 3 else "Legit Website"
        print(f"Status: {status}")
        print(f"Number of misspelled words: {len(misspelled)}")
        if misspelled:
            print(f"Misspelled words: {', '.join(misspelled)}")