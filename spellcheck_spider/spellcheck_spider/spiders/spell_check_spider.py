import scrapy
from spellchecker import SpellChecker
import re
import lxml.html.clean
import logging

# Disable all logging
logging.disable(logging.CRITICAL)

class SpellCheckSpider(scrapy.Spider):
    name = 'spell_check_spider'

    def start_requests(self):
        # Get the URL from the command-line argument
        url = getattr(self, 'url', None)
        if url is not None:
            yield scrapy.Request(url, self.parse)
        else:
            self.logger.error('URL not provided. Use the -a option to specify the URL. Example: scrapy crawl spell_check_spider -a url=https://www.example.com')

    def parse(self, response):
        spell = SpellChecker()
        cleaner = lxml.html.clean.Cleaner(style=True, scripts=True, javascript=True, comments=True, inline_style=True, links=True, meta=False, page_structure=False, processing_instructions=True, embedded=False, frames=False, forms=False, annoying_tags=False, remove_tags=None, allow_tags=None, kill_tags=None, remove_unknown_tags=True, safe_attrs_only=True)
        clean_html = cleaner.clean_html(response.text)
        text = ' '.join(lxml.html.fromstring(clean_html).xpath('//text()'))
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        misspelled = spell.unknown(words)

        status = "Scam website" if len(misspelled) > 100 else "Legit Website"
        print(f"Status: {status}")
        print(f"Number of misspelled words: {len(misspelled)}")
        if misspelled:
            print(f"Misspelled words: {', '.join(misspelled)}")